import json

import requests

from api.models import ProceedBlogger
from api.services import methods
from flood.modules.BaseFloodModel import BaseFloodModel
from flood.services.global_service import url_normalize
from main.models import Blogger, Post
from parsing.NovemberParsing.url_to_s3 import UrlToS3
from parsing.ParsingModules.ParsingModule import time_print


def clean_to_json(line: str):
    try:
        if line[0] != '{':
            index = line.find(':{')
            return line[index + 1:]
    except:
        pass
    return line


class ProfileDetail(BaseFloodModel):
    @classmethod
    async def from_file(cls, response: requests.Response, blogger_login: str = None, prc_blogger=True):
        response.encoding = 'utf-8'
        i = clean_to_json(response.text)

        data: dict = json.loads(i)['user']

        if blogger_login is None:
            blogger_login = data.get('username')

        blogger = Blogger.objects.get(login=blogger_login, social_network_type_id=3)

        blogger.login = data.get('username')
        blogger.name = str(data.get('full_name')).replace('й', 'й')
        if blogger.social_id is None or len(blogger.social_id) < 1:
            blogger.social_id = data.get('pk')

        blogger.status_id = 2 if data.get('is_private') else 1
        blogger.avatar = f'{blogger.social_id}__{blogger.login}'

        hd_profile_pic_url_info: dict = data.get('hd_profile_pic_url_info')
        url: str = hd_profile_pic_url_info.get('url')
        url = url_normalize(url)
        avatar_dct = {url: blogger.avatar}

        time_print(blogger_login, 'avatar download')
        await UrlToS3.downloader(avatar_dct)
        time_print(blogger_login, 'avatar done')

        blogger.verification_type = 1 if data.get('is_verified') else None
        blogger.post_default_count = data.get("media_count")
        blogger.default_total = data.get('follower_count')
        blogger.following = data.get('following_count')
        blogger.bio = data.get('biography')
        blogger.external_link = data.get('external_url')

        time_print(blogger_login, blogger.er)

        blogger.save()
        time_print(blogger_login, 'done all')
