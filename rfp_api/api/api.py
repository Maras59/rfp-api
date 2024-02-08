from collections import defaultdict

import pandas as pd
from django.http import JsonResponse
from rest_framework.views import APIView

from rfp_api.models import Answer, Organization, Question

from .milvus_index import MilvusConnectionSecrets, MilvusService

credentials = MilvusConnectionSecrets(user="username", password="password", host="standalone")
index = MilvusService(credentials, reset=True)

# temp insert
df = pd.read_csv("qa-pairs.csv")
df["text"] = df["question"]
rows = []
org = Organization.objects.create(name="default")
for row in df.to_dict(orient="records"):
    answer = Answer.objects.create(text=row["answer"], owner_organization=org)
    question = Question.objects.create(text=row["text"], answer=answer)
    row["id"] = question.id
    rows.append(row)
df = pd.DataFrame(rows)
index.insert(df)


class Inference(APIView):
    def get(self, request) -> JsonResponse:
        payload = request.data
        if not (question := payload.get("question")):
            return JsonResponse({"res": "No question found in the payload"})

        return_count = int(request.GET.get("count", 2))
        threshold = float(request.GET.get("threshold", 0.5))

        query_results = index.search(question, k=10, threshold=threshold)

        # get nearest neighbor
        classes = defaultdict(int)
        for item in query_results:
            question = Question.objects.get(id=item.question_id)
            classes[question.answer.id] += item.score

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        question_ids = sorted_classes[:return_count]

        answers = []
        for question_id, score in question_ids:
            answer = Answer.objects.get(id=question_id)
            question = Question.objects.get(answer=answer)
            answers.append({"similar_question": question.text, "answer": answer.text, "score": score})

        return JsonResponse(answers, safe=False)
