from rest_framework import serializers

from .models import Articles

class ArticlesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Articles
        fields = [
            "url"
        ]
        def create(self, validated_data):
            return Articles.objects.create(**validated_data)