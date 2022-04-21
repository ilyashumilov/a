from django.contrib import admin
from django.db import models
from django.db.models import Sum, F, Func
from import_export import resources
#
# Register your models here.
from import_export.admin import ImportExportModelAdmin

from main.models import Blogger, Post, Subscriber
from api.models import ProceedBlogger, SocialNetwork


class BloggerCsv(resources.ModelResource):
    class Meta:
        model = Blogger
        fields = Blogger.open_fields
        # fields='__all__'


class BloggerFilterBySocialNetwork(admin.SimpleListFilter):
    title = 'By social_network_id'

    parameter_name = 'social_network_id'

    def lookups(self, request, model_admin):
        return (SocialNetwork.objects.all().values_list('id', 'name'))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(social_network_type__id=self.value())
        return queryset


class BloggerAdmin(ImportExportModelAdmin):
    resource_class = BloggerCsv
    list_display = [*Blogger.open_fields, 'catgs']
    search_fields = ('id', '=login', 'social_id')
    list_filter = (
        BloggerFilterBySocialNetwork,
        ("post_default_count", admin.EmptyFieldListFilter),
        ("subscribers_count", admin.EmptyFieldListFilter),
        ("following", admin.EmptyFieldListFilter),
        ("default_total", admin.EmptyFieldListFilter),
        ("age", admin.EmptyFieldListFilter),
    )

    def get_queryset(self, request):
        qs = super(BloggerAdmin, self).get_queryset(request)
        # qs = qs.annotate(field_lower=Func(F('categories'), function='CARDINALITY'))
        qs = qs.annotate(
            field_len=Func(F('categories'), function='CARDINALITY', output_field=models.IntegerField()))
        # a.objects.annotate(items=Array(b_sub)).aggregate(Sum(items))
        # Blogger.objects.filter().annotate(field_lower=Func(F('categories'), function='UNNEST'))

        return qs

    def catgs(self, x: Blogger):
        return x.categories

    catgs.admin_order_field = 'field_len'


admin.site.register(Blogger, BloggerAdmin)


class ProceedBloggerCsv(resources.ModelResource):
    class Meta:
        model = ProceedBlogger
        fields = ProceedBlogger.open_fields
        # fields='__all__'


class ProceedBloggerAdmin(ImportExportModelAdmin):
    resource_class = BloggerCsv
    list_display = ProceedBlogger.open_fields
    search_fields = ('id', 'login', 'social_id')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.select_related('city', 'verification_type', 'country', 'gender') \
            .filter(author=request.user)


admin.site.register(ProceedBlogger, ProceedBloggerAdmin)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'blogger_id', 'blogger', 'post_id', 'post_login', 'likes_count',
        'comments_count', 'date', 'text', 'photos_url')
    search_fields = ('id', 'blogger', 'post_id')


admin.site.register(Post, PostAdmin)




# class ProceedSubscriber(admin.ModelAdmin):
#     list_display = Subscriber.open_fields
#     search_fields = ('id', 'social_id', 'login')
#
#
# admin.site.register(Subscriber, ProceedSubscriber)
