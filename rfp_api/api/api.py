from django.http import JsonResponse
from rest_framework.views import APIView
from source.milvus_index import MilvusService


class Inference(APIView):

    def get(self, request: dict):
        index = MilvusService()
        if param := request.GET.get("q", None):
            return JsonResponse({"res": index.inference(param)})
        else:
            return JsonResponse({"res": "No query found"})
