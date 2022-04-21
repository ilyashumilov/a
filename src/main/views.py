from django.shortcuts import render
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.models import SocialNetwork
from main import services, extract_service_v2
from main.extract_service import by_login, writer_excel, by_link, writer_excel_zip
from main.extract_service_v2 import another_socials_append
from main.models import Blogger


@api_view(['GET'])
def update_blogger(request, blogger_login: str):
    try:

        # WorkInfoLogs.objects.create(text=f'{blogger_login} to upd')
        # message = services.create_one_time_parsing(blogger_login, task_type=HypeTask.one_time)
        message = services.create_new_parsing_microservice(blogger_login)
    except Exception as e:
        # WorkInfoLogs.objects.create(f'ERROR {blogger_login}')
        message = {"message": "Нет такого блогера"}
    return Response(message)


def from_db_view(request):
    if request.method == 'POST':
        t = request
        result = dict(request.POST)

        text = by_login(result)
        response = writer_excel(text)
        return response

    return render(request, 'index.html')


def from_db_view_socials(request):
    context = {}
    if request.method == 'POST':
        t = request
        result = dict(request.POST)

        text = by_login(result, int(result['socials_network_id'][0]))
        response = writer_excel(text)
        return response
    else:
        socials = SocialNetwork.objects.all().order_by('id')
        context['socials'] = socials

    return render(request, 'socials.html', context=context)


def from_db_view_socials_links(request):
    context = {}
    if request.method == 'POST':
        t = request
        result = dict(request.POST)

        text = by_link(result, int(result['socials_network_id'][0]))
        response = writer_excel(text)
        return response
    else:
        socials = SocialNetwork.objects.all().order_by('id')
        context['socials'] = socials

    return render(request, 'socials.html', context=context)


def from_db_view_global(request):
    if request.method == 'POST':
        result = dict(request.POST)
        print(result)
        texter = services.get_from_request(result.get('texter'))
        login_or_link = services.get_from_request(result.get('LoginOrLink'))
        params = []
        data = []
        social_network_type_id = services.get_from_request(result.get('social_network_type_id', None))
        social_network_type_id = None if social_network_type_id == 'all_values' else social_network_type_id

        for key, value in result.items():
            key: str
            if key.startswith('_'):
                v = services.get_from_request(value)
                if v == 'another_socials':
                    another_socials_append(params, social_network_type_id)
                else:
                    params.append(v)

        social_network_type_id = services.get_from_request(result.get('social_network_type_id', None))
        social_network_types = []
        if social_network_type_id == 'all_values':
            social_network_types += list(SocialNetwork.objects.values_list('id', flat=True))
        else:
            social_network_types.append(social_network_type_id)

        for social_network_type_id in social_network_types:
            data += extract_service_v2.extract_global(texter, login_or_link, params, social_network_type_id)

        if len(data) > 1000:
            response = writer_excel_zip(data)
        else:
            response = writer_excel(data)
        return response
    else:
        socials = SocialNetwork.objects.all().order_by('id')
        params = Blogger.get_params()

        context = dict(socials=socials, params=params)

    return render(request, 'from_db_global.html', context=context)


# def from_db_view_global(request):
#     if request.method == 'POST':
#         result = dict(request.POST)
#         texter = services.get_from_request(result.get('texter'))
#         login_or_link = services.get_from_request(result.get('LoginOrLink'))
#         params = []
#         for key, value in result.items():
#             key: str
#             if key.startswith('_'):
#                 v = services.get_from_request(value)
#                 params.append(v)
#         social_network_type_id = services.get_from_request(result.get('social_network_type_id', None))
#
#         data = extract_service_v2.extract_global(texter, login_or_link, params, social_network_type_id)
#
#         if len(data) > 1000:
#             response = writer_excel_zip(data)
#         else:
#             response = writer_excel(data)
#         return response
#
#     else:
#         socials = SocialNetwork.objects.all().order_by('id')
#         params = Blogger.get_params()
#
#         context = dict(socials=socials, params=params)
#
#     return render(request, 'from_db_global.html', context=context)


def all_from_db(request):
    t = request
    result = dict(request.POST)

    text = all_from_db(result)
    response = writer_excel(text)
    return response
