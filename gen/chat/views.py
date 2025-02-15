from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import MessageSerializer
import requests


def get_emotion_response(text):
    # Здесь можно сделать запрос к нейросети
    # Пример запроса к внешнему API нейросети:
    response = requests.post("https://some-neural-network-api.com", json={"text": text})
    return response.json().get("response", "Извините, ошибка")


class MessageView(APIView):
    def post(self, request):
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            # Здесь можно подключить нейросеть для обработки сообщения
            response_data = {"response": "Ваше сообщение получено!"}
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)