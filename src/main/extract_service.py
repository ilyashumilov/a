import zipfile
from datetime import datetime
from io import BytesIO
from typing import List

from django.db.models import Q
from django.http import HttpResponse

from api.services import methods
from main.models import Blogger, Post


def options_to_params(options):
    options_new = add_options(options)
    text: str = options['texter'][0]
    accounts = text.lower().strip().replace('\r', '').replace(' ', '').split('\n')
    accounts = [i.replace('instagr.am/', '').replace('https://www.instagram.com/', '').replace('/', '') for i in
                accounts]
    dct = {}
    for i in accounts:
        dct[i] = 0
    return options_new, accounts, dct


def options_to_params_link(options):
    options_new = add_options(options)
    text: str = options['texter'][0]
    accounts = text.strip().replace('\r', '').replace(' ', '').split('\n')
    dct = {}
    for i in accounts:
        dct[i] = 0
    return options_new, accounts, dct


def by_login(options: dict, social_network_id=None):
    options_new, accounts, dct = options_to_params(options)

    if social_network_id is None:
        blogger_data = query_get(Q(login__in=accounts), options_new, dct)
    else:
        blogger_data = query_get(Q(login__in=accounts, social_network_type_id=social_network_id), options_new, dct)

    return line_per_method(1, options_new, blogger_data, dct)


def by_link(options: dict, social_network_id=None):
    if 'link_from' not in values_options:
        values_options.append('link_from')
    options_new, accounts, dct = options_to_params_link(options)
    options_new.append('link_from')

    if social_network_id is None:
        blogger_data = query_get(Q(link_from__in=accounts), options_new, dct)
    else:
        blogger_data = query_get(Q(link_from__in=accounts, social_network_type_id=social_network_id), options_new, dct)
    result = line_per_method_link(1, options_new, blogger_data, dct)
    try:
        del values_options[values_options.index('link_from')]
    except:
        pass
    return result


def all_from_db(options: dict):
    options_new, accounts, dct = options_to_params(options)

    bloggers = Blogger.objects.all()

    return line_per_method(1, options_new, bloggers, dct)


def line_per_method(indexer, options_new, bloggers_data: List[dict], dct):
    all_lines = []
    all_lines.append(options_new)
    for dct__ in bloggers_data:
        line = []
        for key, value in dct__.items():
            line.append(str(value))
        all_lines.append(line)
        try:
            dct[dct__['login'].lower()] += 1
        except:
            continue

    for i, v in dct.items():
        if v == 0:
            t = ['', i]
            t.extend(['' for _ in range(len(options_new) - 3)])
            t.append('НЕТ В БД')
            all_lines.append(t)
    return all_lines


def line_per_method_link(indexer, options_new, bloggers_data: List[dict], dct):
    all_lines = []
    all_lines.append(options_new)
    for dct__ in bloggers_data:
        line = []
        for key, value in dct__.items():
            line.append(str(value))
        all_lines.append(line)
        try:
            dct[dct__['link_from']] += 1
        except:
            continue

    for i, v in dct.items():
        if v == 0:
            t = ['', i]
            t.extend(['' for _ in range(len(options_new) - 3)])
            t.append('НЕТ В БД')
            all_lines.append(t)
    return all_lines


values_options = ['post_default_count', 'priority', 'categories', 'city', 'country', 'gender',
                  'subscribers_count',
                  'verification_type', 'following', 'status_id', 'name', 'ER12', 'likes', 'comments', 'file_from_info']


def add_options(options: dict):
    options_values: List[str] = ['id', 'login', 'social_id']
    for k, v in options.items():
        k: str
        v: str
        if k.startswith('_'):
            index = int(k.replace('_', ''))
            options_values.append(values_options[index - 1])
    return options_values


def query_get(q_: Q, options: List[str], accounts: dict, ):
    data = []
    for blogger in Blogger.objects.filter(q_):
        blg_data = {}
        posts = Post.objects.filter(blogger_id=blogger.id).order_by('-date')

        for i in options:
            if i in ('ER12', "likes", 'comments'):
                continue
            blg_data[i] = str(blogger.__getattribute__(i))

        if 'ER12' in options:
            posts_ = posts[:12]
            likes = sum([i.likes_count for i in posts_])
            comments = sum([i.comments_count for i in posts_])
            er = methods.calculate_er_new__test(likes, comments, blogger)
            blg_data['ER12'] = str(er)
        if 'likes' in options:
            likes = sum([i.likes_count for i in posts])
            blg_data['likes'] = str(likes)
        if 'comments' in options:
            comments = sum([i.comments_count for i in posts])
            blg_data['comments'] = str(comments)

        data.append(blg_data)
    return data


def generate_zip(filename, file):
    mem_zip = BytesIO()

    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, file)

    return mem_zip.getvalue()


def writer_excel(list_of_lists):
    import pandas as pd
    df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        # Set up the Http response.
        name = datetime.now().strftime('%H:%M__%d.%m')
        filename = f'{name}.xlsx'
        response = HttpResponse(
            b.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response


# filename = f'{name}.xlsx'
#
#         generate_zip(filename, b.getvalue())

def writer_excel_zip(list_of_lists):
    import pandas as pd
    df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
    with BytesIO() as b:
        # Use the StringIO object as the filehandle.
        writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1')
        writer.save()
        # Set up the Http response.
        name = datetime.now().strftime('%H:%M__%d.%m')
        filename = f'{name}.xlsx'
        b_data = b.getvalue()
    zip_data = generate_zip(filename, b_data)
    response = HttpResponse(
        zip_data,
        content_type='application/zip'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % f'{name}.zip'
    return response
