import json

from django.utils import timezone
from collections import namedtuple


def device_timestamp_method(device_timestamp: int):
    device_timestamp = str(device_timestamp)[:len('1645532316')]
    return timezone.datetime.fromtimestamp(int(device_timestamp))


def choose(json_data: dict):
    if 'carousel_media' in json_data:
        return json_data.get('carousel_media')[0].get('image_versions2').get('candidates')[0].get('url')
    elif 'image_versions2' in json_data:
        return json_data.get('image_versions2').get('candidates')[0].get('url')
    raise Exception()


def get_caption(json_data: dict):
    if 'caption' in json_data and json_data.get('caption') is not None:
        text = json_data.get('caption')['text']
    else:
        text = ""
    return text


def get_user(json_data: dict):
    user: dict = json_data.get('user')
    social_id = user.get('pk')
    login = user.get('username')
    return login, social_id


def get_location(json_data: dict):
    if 'location' not in json_data:
        return dict()
    location: dict = json_data.get('location')
    keys = ('city', 'address', 'name', 'short_name')
    city_name = None
    for key in keys:
        t = location.get(key, None)
        if t is not None and len(t) > 1 and t != "":
            city_name = t
            break
    city_id = location.get('pk')

    lat = location.get('lat', None)
    lng = location.get('lng', None)
    if lat is None or lng is None:
        latitude_longitude = dict()
    else:
        latitude_longitude = f'{lat};{lng}'

    return dict(city_id=city_id, city_name=city_name, latitude_longitude=latitude_longitude)


PostNamedTuple = namedtuple('PostNamedTuple', ['post_id', 'post_login', 'date', 'comments_count',
                                               'image', 'views_count', 'likes_count', 'text', 'user', 'location'])


def extract_post(line: str):
    json_data: dict = json.loads(line)
    post_id = json_data.get('code')
    post_login = json_data.get('id')
    date = device_timestamp_method(json_data.get('device_timestamp'))
    comments_count = json_data.get('comment_count', 0)
    image = choose(json_data)
    view_count = json_data.get('view_count', 0)
    like_count = json_data.get('like_count', 0)
    text = get_caption(json_data)
    user = get_user(json_data)
    location = get_location(json_data)
    return PostNamedTuple(post_id, post_login, date, comments_count, image,
                          view_count, like_count, text, user, location)


def extract_all_posts_list(text: str):
    buffer = []
    for line in text.strip().split('\n'):
        try:
            buffer.append(extract_post(line))
        except Exception as e:
            print(line)
    return buffer


def extract_all_posts(text: str):
    dct = {}
    addresses = {}
    last_user = None
    for line in text.strip().split('\n'):
        try:
            data = extract_post(line)
            dct[data.post_id] = data
            last_user = data.user
            if data.location is not None and len(data.location) > 0:
                addresses[data.location['city_id']] = data.location
        except Exception as e:
            print(e)
            print(line)
    return dct, last_user, addresses


if __name__ == '__main__':

    with open('/Users/gilyazov/Downloads/navalny.txt', 'r', encoding='utf-8') as f:
        data = f.read().split('\n')
    for i in data:
        extract_post(i)
        break

    # buffer = []
    # for i in data:
    #     if 'location' in i:
    #         json_data = json.loads(i)
    #         l = json_data.get('location')
    #
    #         buffer.append(l)
    # print(len(buffer))
    # print(json.dumps(buffer, ensure_ascii=False))
