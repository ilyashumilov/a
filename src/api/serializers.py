from rest_framework import serializers

from api.models import ProceedBlogger
from main.models import Blogger
from rest.api.social.services.blogger_service import is_blogger_verify, blogger_gender, blogger_status


class BloggerSerializer(serializers.ModelSerializer):
    avatar = serializers.ReadOnlyField(source='avatar_link')
    social_network_type = serializers.IntegerField(source='social_network_type_id')
    city = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    def get_city(self, obj: Blogger):
        return None if obj.address is None else obj.address.original_city

    def get_country(self, obj: Blogger):
        return None if obj.address is None else obj.address.original_country

    class Meta:
        model = ProceedBlogger
        fields = '__all__'


class SimpleBloggerSerializer(serializers.ModelSerializer):
    avatar = serializers.NullBooleanField(default=None)

    class Meta:
        model = Blogger
        fields = '__all__'


class RangeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    start = serializers.CharField(max_length=255, required=False)
    end = serializers.CharField(max_length=255, required=False)


class SearchSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=255, required=False)
    name = serializers.CharField(max_length=255, required=False)
    social_network_type_id = serializers.IntegerField(required=False)
    subscribers_count_gte = serializers.IntegerField(required=False)
    subscribers_count_lte = serializers.IntegerField(required=False)
    gender__name = serializers.CharField(max_length=255, required=False)
    engagement_rate__gte = serializers.IntegerField(required=False)
    engagement_rate__lte = serializers.IntegerField(required=False)
    age__gte = serializers.IntegerField(required=False)
    age__lte = serializers.IntegerField(required=False)

    sort_by = serializers.CharField(max_length=100, required=False)


def name_test(*args, **kwargs):
    print(args)
    print(kwargs)
    print()


class GlobalTopSerializer(serializers.ModelSerializer):
    is_verify = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_is_verify(self, obj):
        return is_blogger_verify(obj)

    def get_avatar(self, obj):
        return obj.avatar_link

    def get_gender(self, obj):
        return blogger_gender(obj)

    def get_status(self, obj):
        return blogger_status(obj)

    class Meta:
        model = Blogger
        exclude = ('verification_type', 'created_at', 'is_photo_analyzed', 'phone_number', 'email', 'is_advertiser',
                   'file_from_info', 'parsing_updated_at', 'parsing_measurement', 'parsing_status', 'link_from')


class InstagramTopSerializer(serializers.ModelSerializer):
    is_verify = serializers.SerializerMethodField()

    def get_is_verify(self, obj):
        return is_blogger_verify(obj)

    def get_category(self, obj):
        return obj.category.name

    class Meta:
        model = Blogger
