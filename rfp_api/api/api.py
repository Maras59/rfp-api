from collections import defaultdict
from django.http import JsonResponse
from rest_framework.views import APIView
from source.milvus_index import MilvusConnectionSecrets, MilvusService

credentials = MilvusConnectionSecrets(user="username", password="password")
index = MilvusService(credentials)

class Inference(APIView):
    def get(self, request: dict):
        if request.GET.get("q") is None:
            return JsonResponse({"res": "No query parameter found"})
        
        return_count = int(request.GET.get("count", 5))

        query_results = index.search(request.GET.get("q", None))
        
        # get nearest neighbor
        classes = defaultdict(int)
        for item in query_results:
            question = self.db.get_question_by_id(item.question_id)
            score = 1 - item.score
            classes[question.answer_id] += score

        # create list of tuples (score, class) and sort it
        sorted_classes = sorted(classes.items(), key=lambda x: x[1], reverse=True)
        top_answers = sorted_classes[:return_count]

        return JsonResponse({"res": top_answers})