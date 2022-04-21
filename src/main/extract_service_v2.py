from datetime import datetime
from io import BytesIO
from typing import List

from django.db.models import Q
from django.http import HttpResponse

from api.models import SocialNetwork
from api.services import methods
from main.models import Blogger, Post


def extract_by_login(text: str, social_network_type_id=None):
    logins = text.lower().strip().replace('\r', '').replace(' ', '').split('\n')
    logins = [i.replace('instagr.am/', '').replace('https://www.instagram.com/', '').replace('/', '') for i in logins]
    dct = {}
    for i in logins:
        dct[i] = 0

    if social_network_type_id is None:
        q = (Q(login__in=logins))
    else:
        q = (Q(login__in=logins) & Q(social_network_type_id=social_network_type_id))

    return logins, dct, q


def extract_by_link(text: str, social_network_type_id=None):
    links = text.strip().replace('\r', '').replace(' ', '').split('\n')
    dct = {}
    for i in links:
        dct[i] = 0

    if social_network_type_id is None:
        q = (Q(link_from__in=links))
    else:
        q = (Q(link_from__in=links) & Q(social_network_type_id=social_network_type_id))

    return links, dct, q


login_or_link_dct = {'Login': extract_by_login, 'Link': extract_by_link}
login_or_link_field = {'Login': 'login', 'Link': "link_from"}


def extract_global(text: str, by_what: str, params_: list, social_network_type_id: int):
    params = ['id', 'login']
    if by_what == 'Link':
        params.append('link_from')
    params.extend(params_)

    data, dct, q = login_or_link_dct[by_what](text, social_network_type_id)
    blg_data = get_query_by_q(q, params, by_what)
    result = pre_export_to_excel(blg_data, dct, params, login_or_link_field[by_what])
    return result


def pre_export_to_excel(blg_data, dct, params, field_name):
    all_lines = []
    all_lines.append(params)
    for dct__ in blg_data:
        line = []
        [line.append(str(dct__[param])) for param in params]
        all_lines.append(line)
        try:
            dct[dct__[field_name]] += 1
        except:
            continue

    for i, v in dct.items():
        if v == 0:
            t = ['', i]
            t.extend(['' for _ in range(len(params) - 3)])
            t.append('НЕТ В БД')
            all_lines.append(t)
    return all_lines


def get_query_by_q(q_, params: list, by_what):
    data = []

    another_socials = dict()
    for i in params:
        if "another_socials" in i:
            another_socials[i] = i[16:]

    for blogger in Blogger.objects.filter(q_):
        blg_data = {}

        for i in params:
            if i in ('ER12', "LIKES", 'COMMENTS') or "another_socials" in i:
                continue
            blg_data[i] = str(blogger.__getattribute__(i))

        if another_socials:
            ln: dict = blogger.__getattribute__("another_socials")
            for another_social_key, another_social in another_socials.items():
                try:
                    another_social_value = ln.get(another_social)
                    if by_what == "Link":
                        if another_social == 'instagram':
                            another_social_value = f'https://www.instagram.com/{another_social_value}/'
                        elif another_social == 'facebook':
                            another_social_value = f'https://www.facebook.com/{another_social_value}/'
                        elif another_social == 'vk':
                            another_social_value = f'https://vk.com/{another_social_value}/'
                        elif another_social == 'youtube':
                            another_social_value = f'https://www.youtube.com/{another_social_value}/'
                        elif another_social == 'twitter':
                            another_social_value = f'https://twitter.com/{another_social_value}/'
                        elif another_social == 'tiktok':
                            another_social_value = f'https://www.tiktok.com/@{another_social_value}/'
                except Exception:
                    another_social_value = ''

                blg_data[another_social_key] = another_social_value

        if 'ER12' in params or "LIKES" in params or "COMMENTS" in params:
            posts = Post.objects.filter(blogger_id=blogger.id).order_by('-date')

            if 'ER12' in params:
                posts_ = posts[:12]
                likes = sum([i.likes_count for i in posts_])
                comments = sum([i.comments_count for i in posts_])
                er = methods.calculate_er_new__test(likes, comments, blogger)
                blg_data['ER12'] = str(er)
            if 'LIKES' in params:
                likes = sum([i.likes_count for i in posts])
                blg_data['LIKES'] = str(likes)
            if 'COMMENTS' in params:
                comments = sum([i.comments_count for i in posts])
                blg_data['COMMENTS'] = str(comments)

        data.append(blg_data)
    return data


def another_socials_append(params, social_network_type_id):
    another_socials = list(SocialNetwork.objects.exclude(id=social_network_type_id).values_list('name', flat=True))
    another_socials_values = [f'another_socials_{another_social}' for another_social in another_socials]
    [params.append(another_social) for another_social in another_socials_values]
    return another_socials_values
