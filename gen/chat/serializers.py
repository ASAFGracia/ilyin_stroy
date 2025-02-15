from rest_framework import serializers

class MessageSerializer(serializers.Serializer):
    sender = serializers.CharField(max_length=100)
    text = serializers.CharField()