from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView

class Inference(APIView):

    def get(self, request):
        param = request.GET.get('q', '')
        return JsonResponse({'res' : ["Query Parameter: {param}"]})