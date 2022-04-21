from django.db.models import Q

from main.models import Blogger


def relevant_by_er(blogger: Blogger, delta: float):
    er_ = blogger.er
    er_min = er_ - (er_ * delta)
    er_max = er_ + (er_ * delta)
    q_ = Q(engagement_rate__gte=er_min) & Q(engagement_rate__lte=er_max)
    return q_


def relevant_by_categories(blogger: Blogger, delta: float):
    q_ = Q(categories__overlap=blogger.categories)
    return q_


def relevant_by_subscribers(blogger: Blogger, delta: float):
    dt_ = blogger.dt
    dt_min = dt_ - int(dt_ * delta)
    dt_max = dt_ + int(dt_ * delta)
    q_ = Q(default_total__gte=dt_min) & Q(default_total__lte=dt_max)
    return q_


methods_of_relevant_type = {0: relevant_by_er,
                            1: relevant_by_categories,
                            2: relevant_by_subscribers}


def check_word_rus(word: str):
    alf = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    word = str(word).lower() + " "
    size = len(word)
    counter = 0

    for i in word.lower():
        if i in alf:
            counter += 1

    return counter // size > size // 2


def check_word_eng(word: str):
    alf = list('abcdefghijklmnopqrstuvwxyz')
    word = str(word).lower() + " "
    size = len(word)
    counter = 0

    for i in word:
        if i in alf:
            counter += 1

    return counter // size > size // 2


def check_word_oth(word: str):
    alf = list('абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz')
    word = str(word).lower() + " "
    size = len(word)
    counter = 0

    for i in word:
        if i in alf:
            counter += 1

    return counter // size < size // 2


check_word_choose = {'eng': check_word_eng, 'rus': check_word_rus, 'oth': check_word_oth}


def check_word(word: str):
    if check_word_eng(word):
        return 'eng'
    elif check_word_rus(word):
        return 'rus'
    else:
        return 'oth'
