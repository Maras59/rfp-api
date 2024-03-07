from collections import defaultdict

import ollama
import pandas as pd
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.http import JsonResponse
from rest_framework.views import APIView

from rfp_api.models import Answer, Organization, Question

from .milvus_index import MilvusConnectionSecrets, MilvusService

credentials = MilvusConnectionSecrets(user="username", password="password", host="standalone")
index = MilvusService(credentials)
llm = ollama.Client("http://ollama:11434")
llm.pull("gemma:2b")


@receiver(pre_delete, sender=Question)
def on_question_delete(sender, instance, **kwargs):
    index.drop_question(instance.id)


@receiver(pre_save, sender=Question)
def on_question_update(sender, instance, **kwargs):
    if instance.pk and not instance._state.adding:  # If the primary key exists and not adding a new instance
        index.update_question(instance.id, instance.text)


@receiver(post_save, sender=Question)
def on_question_insert(sender, instance, created, **kwargs):
    if created:
        index.insert_question(instance.id, instance.text)


class Inference(APIView):
    def post(self, request) -> JsonResponse:
        payload = request.data
        if not (user_question := payload.get("question")):
            return JsonResponse({"res": "No question found in the payload"})

        return_count = int(payload.get("count", 2))
        threshold = float(payload.get("threshold", 0.4))
        use_llm_synthesis = payload.get("use_llm_synthesis", False)

        query_results = index.search(user_question, k=10, threshold=threshold)

        # get nearest neighbor
        classes = defaultdict(int)
        for item in query_results:
            question = Question.objects.get(id=item.question_id)
            classes[question.answer.id] += item.score

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        answer_ids = sorted_classes[:return_count]

        answers = []
        for answer_id, score in answer_ids:
            answer = Answer.objects.get(id=answer_id)
            question = Question.objects.get(answer=answer)
            answers.append(
                {"similar_question": question.text, "answer": answer.text, "score": score, "answer_id": answer_id}
            )

        if use_llm_synthesis:
            answers_string = " --- ".join(map(lambda x: x["answer"], answers))
            prompt = """You will be provided a number of possible answers to the given question separated by "---" as context. Using the given context, answer the question at the end. When you use an answer, retain as many details from that answer as necessary.

<Examples>

Example Possible Answers 1: 10,432 employees in the system, but only 543 are ready for a new project at this time.
Example Question 1: How many active employees do you have?
Example Answer 1: We have 10,432 employees in our system with 543 ready for a new project.

Example Possible Answers 2: We give our employees 100 days of vacation per year to ensure they are focused during work. --- We train our employees daily on locking their computer.
Example Question 2: What are your security protocols?
Example Answer 2: We train our employees daily on security protocols. Our security protocols include providing 100 days of vacation per employee to ensure they are focused.

Example Possible Answers 3: Red
Example Question 3: What is Partner Personnel's logo color?
Example Answer 3: Partner Personnel's logo color is red.

<Actual>

Possible Answers: {answers_context}
Question: "{question}"
Answer:""".format(
                answers_context=answers_string, question=user_question
            )
            print(prompt)
            response = llm.chat(model="gemma:2b", messages=[{"role": "user", "content": prompt}])
            answer = response["message"]["content"]
        else:
            answer = answers[0]["answer"]

        response = {"possible_answers": answers, "question": user_question, "answer": answer}

        return JsonResponse(response, safe=False)


class Init(APIView):
    def get(self, request) -> JsonResponse:
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
        return JsonResponse({"res": "API is running"})
