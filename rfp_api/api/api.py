from collections import defaultdict
from django.http import JsonResponse
import pandas as pd
from rest_framework.views import APIView
from .milvus_index import MilvusConnectionSecrets, MilvusService
from rfp_api.models import Answer, Question

credentials = MilvusConnectionSecrets(user="username", password="password", host="standalone")
index = MilvusService(credentials, reset=True)

# temp insert
df = pd.read_csv("qa-pairs.csv")
df["id"] = df.index
df["text"] = df["question"]
index.insert(df)


class Inference(APIView):
    def get(self, request: dict) -> JsonResponse:
        if request.GET.get("q") is None:
            return JsonResponse({"res": "No query parameter found"})
        
        return_count = int(request.GET.get("count", 2))
        threshold = float(request.GET.get("threshold", 0.5))

        query_results = index.search(request.GET.get("q", None), k=10, threshold=threshold)
        
        # get nearest neighbor
        classes = defaultdict(int)
        for item in query_results:
            question = Question.objects.get(id=item.question_id)
            score = 1 - item.score
            classes[question.answer.id] += score

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        question_ids = sorted_classes[:return_count]

        answers = []
        for question_id, score in question_ids:
            answer = Answer.objects.get(id=question_id)
            answers.append({"answer": answer.text, "score": score})

        return JsonResponse({"res": answers})
