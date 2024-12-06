from rest_framework.serializers import ModelSerializer
from .models import Event, EventRegistration
from django.contrib.auth.models import User

class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class EventRegistrationSerializer(ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = ['event', 'user', 'first_name', 'last_name', 'email']


    def create(self, validated_data):
        registration = EventRegistration.objects.create(**validated_data)
        print("Registration created:", registration)
        return registration
