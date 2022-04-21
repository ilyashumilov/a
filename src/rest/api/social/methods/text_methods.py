import re
import string
from collections import defaultdict
from typing import List

import emoji as Emoji

from main.models import Post


def rm_all_not_symb_in_text(text) -> str:
    return_text = []
    reject_symbs = set(list('.,-—'))

    for symb in text:
        if symb in Emoji.UNICODE_EMOJI['en'] or symb in reject_symbs:
            return_text.append(' ')
        else:
            return_text.append(symb)

    return (''.join(return_text)).strip().replace('  ', ' ').strip()


def last_advertisers_method(post: Post, unique: dict):
    def clean(text: str):
        return text.replace('・', ' ').strip().lower().split(' ')[0].split('⠀')[0].replace('@', '')

    def match(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя,')):
        return not alphabet.isdisjoint(text.lower())

    t = set([clean(re.sub(r"@+", "@", k)) for k in set([re.sub(r"(\W+)$", "", j, flags=re.UNICODE) for j in
                                                        set([i for i in post.text.split() if
                                                             i.startswith("@")])])])
    new_set = dict()
    for i in t:
        if len(i) < 100 and not match(i):
            new_set[i] = 0

    return {**unique, **new_set}


def last_advertisers_method_new(post: Post):
    def clean(text: str):
        return text.replace('・', ' ').strip().lower().split(' ')[0].split('⠀')[0].replace('@', '')

    def match(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя,')):
        return not alphabet.isdisjoint(text.lower())

    t = set([clean(re.sub(r"@+", "@", k)) for k in set([re.sub(r"(\W+)$", "", j, flags=re.UNICODE) for j in
                                                        set([i for i in post.text.split() if
                                                             i.startswith("@")])])])
    new_set = dict()
    for i in t:
        if len(i) < 100 and not match(i):
            new_set[i] = 0

    return new_set


def last_advertiser_method_v2(text: str):
    results = re.findall("(^|[^@\w])@(\w{1,30})", text)
    nicknames = defaultdict(int)
    for result in results:
        nicknames[result[1]] += 1

    return nicknames


def tags_method(text: str, hashtags: dict):
    results = re.findall("(^|[^#\w])#(\w{1,30})", text)
    for result in results:
        if result[1] not in hashtags:
            hashtags[result[1]] = 0
        hashtags[result[1]] += 1

    return hashtags


def create_steps(keys: List[str], dct: dict, steps: int):
    for key in list(keys):
        t = dct['work_data'][key]
        dct['work_data'][f'{key}__steps'] = []
        for i in range(steps + 1):
            q = t / steps * i
            dct['work_data'][f'{key}__steps'].append(q)


def capwords(line: str):
    try:
        return line[0].upper() + line[1:]
    except:
        return line


def check_word_exclude(word: str):
    if len(word) < 5:
        return True
    if len(word) > 20:
        return True
    if is_sign_exclude(word):
        return True
    return False


accept_signs = (string.ascii_lowercase + "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" + '-_—.,"' + string.digits)
accept_signs = set(list(accept_signs))


def is_sign_exclude(word):
    for i in word:
        if i not in accept_signs:
            return True
    return False
