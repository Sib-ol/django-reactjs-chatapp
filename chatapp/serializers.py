from rest_framework import serializers
from chatapp.models import ChatMessage
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username","avatar"]


class ChatSerializer(serializers.Serializer):
    chat_id = serializers.UUIDField(read_only=True,source="public_id")
    member = serializers.CharField(write_only=True)
    message = serializers.CharField(write_only=True)
    last_message = serializers.SerializerMethodField()
    last_message_sender = serializers.SerializerMethodField()
    last_date = serializers.CharField(read_only=True)

    class Meta:
        fields = "__all__"

    def get_last_message(self, obj):
        return obj.last_messages
    
    def get_last_message_sender(self, obj):
        return obj.last_messages_sender
    
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        request = self.context["request"]
        profile_image = None

        try:
            if obj.has_group:
                display_name = obj.name.capitalize()
                profile_image = obj.group_profile.url
            else:
                user_qs = obj.chat_user.all().exclude(user=request.user)
                user = user_qs.first().user
                display_name = user.username.capitalize()
                if user.avatar.name:
                    profile_image =  user.avatar.url
        except AttributeError:
            display_name = None
            profile_image = None

        representation['display_name'] = display_name
        representation['chat_profile'] = profile_image
        return representation

class ChatMessageSerializer(serializers.ModelSerializer):
    message_id = serializers.IntegerField(source="id",read_only=True)
    user_details = UserSerializer(source="user.user")

    class Meta:
        model = ChatMessage
        fields = [
            "message_id",
            "message",
            "user_details",
            "read",
            "created_at",
        ]

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

    class Meta:
        fields = ("message",)

class CheckSerializer(serializers.Serializer):
    chat_name = serializers.CharField()

    class Meta:
        fields = ["chat_name"]
