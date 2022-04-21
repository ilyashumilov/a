from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from main.managers import BloggerManager, PostManager, SubscriberManager

args = dict(null=True, blank=True, default=None)


def default_categories():
    return [3]


class Blogger(models.Model):
    objects = BloggerManager()

    login = models.CharField(max_length=255, db_index=True, default=None, null=True)
    social_id = models.CharField(max_length=255, db_index=True, default="")
    name = models.CharField(max_length=255, db_index=True, **args)
    social_network_type_id = models.BigIntegerField(default=3, db_index=True, null=True, blank=True)

    # metrics
    post_default_count = models.IntegerField(**args)
    default_total = models.BigIntegerField(db_index=True, default=0)
    following = models.BigIntegerField(db_index=True, **args)

    # profile info
    status = models.ForeignKey("main.Status", on_delete=models.SET_NULL, **args)  # открыт закрыт архив
    verification_type = models.ForeignKey("main.VerificationType", on_delete=models.SET_NULL, **args)
    avatar = models.CharField(max_length=255, **args)
    bio = models.TextField(**args)
    # category = models.CharField(max_length=255, **args)
    category = models.ForeignKey('main.Category', on_delete=models.SET_NULL, null=True, default=None)
    external_link = models.TextField(**args)

    # profile after parsing
    categories = ArrayField(models.IntegerField(), default=default_categories, null=True, blank=True)
    account_creation_date = models.DateField(**args)
    address = models.ForeignKey('main.Address', on_delete=models.SET_NULL, **args)
    language = models.ForeignKey('main.Language', on_delete=models.SET_NULL, **args)
    is_business_account = models.BooleanField(default=False)

    # proceed data
    gender = models.ForeignKey("main.Gender", on_delete=models.SET_NULL, **args)
    age = models.IntegerField(**args)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, **args)

    # parsing
    parsing_status = models.BooleanField(default=False)
    parsing_measurement = models.PositiveSmallIntegerField(default=0)
    parsing_updated_at = models.DateTimeField(auto_now_add=True)

    # other
    file_from_info = ArrayField(models.CharField(max_length=200, default=None, null=True), default=list)
    link_from = models.CharField(max_length=255, default=None, null=True)
    another_socials = models.JSONField(default=dict)
    is_advertiser = models.BooleanField(default=False)
    advertisers_ids = ArrayField(models.IntegerField(), default=list, null=True, blank=True)

    email = models.CharField(max_length=255, **args)
    phone_number = models.CharField(max_length=255, **args)

    is_photo_analyzed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    open_fields = []

    @staticmethod
    def get_params():
        return ['social_id', 'categories', 'file_from_info', 'link_from', 'another_socials', 'social_network_type_id',
                'post_default_count', 'ER12', 'LIKES', 'COMMENTS', 'default_total', 'following', 'subscribers_count',
                'status_id', 'verification_type_id', 'avatar', 'name', 'age', 'bio', 'external_link', 'phone', 'city',
                'country', 'gender', 'account_creation_date']

    @property
    def avatar_link(self):
        photo = self.avatar
        if photo is None or len(str(photo)) < 2:
            return None
        host = settings.BASE_URL
        return f'http://{host}/api/photo/{photo}/'

    @property
    def dt(self):
        dt_ = self.default_total
        if dt_ is None or dt_ < 1:
            dt_ = 1
        return dt_

    @property
    def er(self):
        if getattr(self, 'er___', None) is not None:
            return float(getattr(self, 'er___', 0.0))

        try:
            er_decimal = self.create_er()
            if er_decimal != self.engagement_rate:
                self.engagement_rate = er_decimal
                self.save(update_fields=['engagement_rate'])
            self.er___ = float(er_decimal)
            return float(er_decimal)
        except:
            return None

    def create_er(self):
        try:
            try:
                posts = self.posts_done[:12]
            except:
                posts = self.posts.filter(is_deleted=False).only('likes_count', 'comments_count').order_by('-date')[:12]
            likes = 0
            comments = 0
            for i in posts:
                likes += i.likes_count
                comments += i.comments_count

            er_ = (((likes + comments) / 12) / self.dt) * 100
            er_ = round(er_, 2)
            if er_ > 100:
                return Decimal('99.99')
            er_decimal = Decimal("{:.2f}".format(er_))
            return er_decimal
        except:
            return 0

    @property
    def name_capitalized(self):
        try:
            line = self.name.split(' ')
            return line[0].upper() + line[1:]
            # words = self.name.split(' ')
            # name_ = ' '.join(list(map(lambda x: x[0].upper()+x[1:], words)))
            # return name_
        except:
            return self.name

    @property
    def social_or_login(self):
        if self.social_id is None or len(str(self.social_id).strip().replace("  ", ' ')) < 1:
            return self.login
        else:
            return self.social_id

    class Meta:
        db_table = 'hype__blogger'
        unique_together = ('social_id', 'social_network_type_id')


class Subscriber(models.Model):
    objects = SubscriberManager()

    login = models.CharField(max_length=255)
    social_id = models.CharField(max_length=255, db_index=True)
    name = models.CharField(max_length=255, db_index=True, **args)
    social_network_type_id = models.BigIntegerField(default=3, db_index=True, null=True, blank=True)

    bloggers = ArrayField(models.BigIntegerField(), default=list)  # index gin

    # metrics
    followers = models.BigIntegerField(**args)
    following = models.BigIntegerField(**args)
    contents = models.BigIntegerField(**args)

    # profile info
    status = models.ForeignKey("main.Status", on_delete=models.SET_NULL, **args)  # открыт закрыт архив
    verification_type = models.ForeignKey("main.VerificationType", on_delete=models.SET_NULL, **args)
    avatar = models.CharField(max_length=255, **args)
    bio = models.TextField(**args)
    category = models.ForeignKey('main.Category', on_delete=models.SET_NULL, null=True, default=None)
    external_link = models.TextField(**args)

    # profile after parsing
    address = models.ForeignKey('main.Address', on_delete=models.SET_NULL, **args)
    language = models.ForeignKey('main.Language', on_delete=models.SET_NULL, **args)
    is_business_account = models.BooleanField(**args)

    # proceed data
    gender = models.ForeignKey("main.Gender", on_delete=models.SET_NULL, **args, db_index=True)
    age = models.IntegerField(**args, db_index=True)

    # other
    email = models.CharField(max_length=255, **args)
    phone_number = models.CharField(max_length=255, **args)

    is_photo_analyzed = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    open_fields = ['id', 'social_id', 'login', 'social_type_id', 'bloggers', 'followers',
                   'following', 'contents', 'name', 'phone', 'email', 'category', 'city',
                   'verification_type', 'updated_at', 'created_at']

    class Meta:
        db_table = 'hype__subscriber'
        unique_together = ('social_id', 'social_network_type_id')


class Post(models.Model):
    objects = PostManager()

    blogger = models.ForeignKey('main.Blogger', related_name='posts', on_delete=models.CASCADE, db_index=True, **args)
    post_id = models.CharField(max_length=255, unique=True)
    post_login = models.CharField(max_length=255)
    photos_url = models.TextField()
    text = models.TextField()
    likes_count = models.IntegerField()
    comments_count = models.IntegerField()
    views_count = models.IntegerField(default=0)
    date = models.DateTimeField()
    is_deleted = models.BooleanField(default=False)

    address = models.ForeignKey('main.Address', on_delete=models.SET_NULL, null=True, default=None)

    proceed_face_data = models.BooleanField(default=False)
    face_data = models.JSONField(default=None, null=True)

    @property
    def date_str(self):
        return f'{self.date.month}.{self.date.year}'

    class Meta:
        db_table = "hype__post"


class Comment(models.Model):
    post = models.ForeignKey("main.Post", related_name='comments', on_delete=models.DO_NOTHING, db_index=True)
    text = models.TextField()
    comment_id = models.CharField(max_length=50)
    commentator_social_id = models.CharField(max_length=255)
    commentator_login = models.CharField(max_length=255)

    emotion_text_type = models.ForeignKey("main.Emotion", on_delete=models.SET_NULL, null=True, default=None)
    emoji = models.JSONField(default=None, null=True)
    is_contain_profanity = models.BooleanField(default=None, null=True)
    is_done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('post_id', 'comment_id')
        db_table = 'hype__comment'


class Like(models.Model):
    post = models.ForeignKey("main.Post", related_name='likes', on_delete=models.DO_NOTHING, db_index=True)
    social_id = models.CharField(max_length=255)
    login = models.CharField(max_length=255)

    class Meta:
        unique_together = ['post_id', 'social_id']
        db_table = 'hype__like'
