import datetime
import itertools
import os.path
import sys
import time
from typing import List

from django.conf import settings
from django.db.models import QuerySet, Q

from main.models import Post, Blogger, Emotion, Comment
from rest.api.social.methods.util_methods import round_
from rest.api.social.services.language_controller import LanguageController

with open(os.path.join(settings.BASE_DIR,'..', r'EMOJIES.txt'), 'r', encoding='utf-8') as f:
    emoji_emotion = f.read().strip().split('\n')

emoji_emotion = {x.split(';')[0]: x.split(';')[1] for x in emoji_emotion}


def comments_method(posts_: QuerySet[Post], month: datetime.date, language='ru'):
    try:
        emotions_graph, emoji, profanity_dct = __comments_method(posts_, month, language)
    except Exception as e:
        emotions_graph = {}
        emoji = {}
        profanity_dct = {"use": 0, 'not_use': 0}

    return emotions_graph, emoji, profanity_dct


def __comments_method(posts_: QuerySet[Post], month: datetime.date, language):
    emotions_dct = {}
    for i in Emotion.objects.all():
        emotions_dct[i.id] = LanguageController.get_field(i, language)

    posts = posts_.filter(date__gte=month)
    posts_date = {}
    emoji = {}
    emotions_graph = {}
    profanity_dct = {"use": 0, "not_use": 0}

    for post in posts:
        t_date = f"{post.date.month}.{post.date.year}"
        posts_date[post.id] = t_date
        emotions_graph[t_date] = dict(comments_count=0, positive=0, neutral=0, negative=0)

    comments = Comment.objects.filter(
        Q(post_id__in=list(posts_date.keys())) & ~Q(emotion_text_type=None)) \
        .only('emotion_text_type_id', 'emoji', 'post_id', 'is_contain_profanity')

    st = time.monotonic()
    print(len(comments))
    print('end time comments', time.monotonic() - st)

    by_comments(comments, emotions_graph, posts_date, emotions_dct, emoji, profanity_dct)

    emoji = dict(sorted(emoji.items(), key=lambda item: item[1], reverse=True))
    emoji = dict(itertools.islice(emoji.items(), 50))
    emoji_with_emotion = {}
    for key, value in emoji.items():
        emoji_with_emotion[key] = dict(emotion=emoji_emotion.get(key, ""), count=value)

    return emotions_graph, emoji_with_emotion, profanity_dct


def by_comments(comments: List[Comment], emotions_graph, posts_date, emotions_dct, emoji, profanity_dct):
    size = 0
    try:
        st = time.monotonic()
        counter = 0
        for comment in comments:
            comment: Comment

            t_graph = emotions_graph[posts_date[comment.post_id]]

            t_graph['comments_count'] += 1
            try:
                t_graph[emotions_dct[comment.emotion_text_type_id]] += 1
            except:
                pass

            for k, v in comment.emoji.items():
                if k not in emoji:
                    emoji[k] = v
                else:
                    emoji[k] += v

            if comment.is_contain_profanity is True:
                profanity_dct['use'] += 1
            elif comment.is_contain_profanity is False:
                profanity_dct['not_use'] += 1
            size += 1
            counter += 1

    except Exception as e:
        print(e)
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

    use_and_not_use_count = profanity_dct['use'] + profanity_dct['not_use']

    print('use', profanity_dct['use'] / use_and_not_use_count)
    print('not_use', profanity_dct['not_use'] / use_and_not_use_count)

    profanity_dct['use'] = round_(profanity_dct['use'] / use_and_not_use_count, 4) * 100
    profanity_dct['not_use'] = round_(profanity_dct['not_use'] / use_and_not_use_count, 4) * 100

    # return emotions_graph, emoji, profanity_dct
