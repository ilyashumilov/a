# from textblob import TextBlob

from main.models import Comment, Post
from django.db.models.functions import TruncDay
# from profanity_filter import ProfanityFilter
# import spacy
# from profanity_rus.helpers import PymorphyProc
#
#
# def profanity_check(comment: Comment):
#     # nlp = spacy.load("en_core_news_sm")
#
#     b = TextBlob(comment.text)
#     lang = b.detect_language()
#     pf = ProfanityFilter(languages=['en', 'ru'])
#     if lang == 'en':
#         comment.is_contain_profanity = pf.is_profane(comment.text)
#     elif lang == 'rus':
#         comment.is_contain_profanity = True if PymorphyProc.test(comment.text) == 1 else False
#     comment.save()
#     return comment.is_contain_profanity
