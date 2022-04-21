import json

from brightdata.models import SubscriberScrappingAvatarInfo
from main.models import Subscriber, SubscriberToBloggerHelpModel
from parsing.ParsingModules.ParsingModule import time_print


async def flood_subs_async_two_column(blogger_id, rows: list):
    dct = {}
    for i in rows:
        social_id, login = i.split(':')
        dct[social_id] = login
    subscribers = Subscriber.objects.filter(social_id__in=list(dct.keys()), social_type_id=3)
    upd = []

    for sub in subscribers:
        if blogger_id not in sub.bloggers:
            sub.bloggers.append(blogger_id)
            upd.append(sub)

        try:
            del dct[sub.social_id]
        except:
            pass

    Subscriber.objects.bulk_update(upd, fields=['bloggers'], batch_size=5_000)
    create = []
    for social_id, login in dct.items():
        create.append(
            Subscriber(social_type_id=3, social_id=social_id, login=login, bloggers=[blogger_id])
        )
    Subscriber.objects.bulk_create(create, batch_size=5_000, ignore_conflicts=True)
    print('len upd',len(upd),'len create',len(create))

async def flood_subs_async(blogger_id, rows: list):
    dct = {}
    avatars = []
    for i in rows:
        pk, login, language, country, json_data = i.split(':', maxsplit=4)
        usr: dict = json.loads(json_data)['user']
        full_name = usr.get('full_name', None)
        is_private = usr.get('is_private', False)
        try:
            hd_profile_pic_url_info = str(usr.get('hd_profile_pic_url_info', '').get('url')).replace(r'\u0026', '&')
        except:
            hd_profile_pic_url_info = None
        biography = usr.get('biography', None)
        posts_count = usr.get('media_count', 0)
        followers = usr.get('follower_count', 0)
        following = usr.get('following_count', 0)
        is_business = usr.get('is_business', False)
        is_verified = 1 if usr.get('is_verified', False) else 2

        dct[pk] = {
            'pk': pk,
            'login': login,
            "followers": followers, "following": following,
            "contents": posts_count, "name": full_name, "bio": biography, "avatar": f'{pk}__{login}',
            "is_business_account": is_business, "verification_type_id": is_verified, 'photo': hd_profile_pic_url_info
        }
    subscribers = Subscriber.objects.filter(social_id__in=list(dct.keys()), social_type_id=3)
    upd = []
    create = []
    dct_copy = dct.copy()
    for subscriber in subscribers:
        t = dct[subscriber.social_id]
        subscriber.followers = t['followers']
        subscriber.following = t['following']
        subscriber.contents = t['contents']
        subscriber.name = t['name']
        subscriber.login = t['login']
        subscriber.bio = t['bio']
        subscriber.avatar = t['avatar']
        subscriber.is_business_account = t['is_business_account']
        subscriber.verification_type_id = t['verification_type_id']
        subscriber.social_type_id = 3
        upd.append(subscriber)
        try:
            del dct[subscriber.social_id]
        except:
            pass
    time_print('upd subs', len(upd))
    Subscriber.objects.bulk_update(upd,
                                     fields=['login', 'followers', 'following', 'social_type_id', 'contents', 'name',
                                             'bio', 'avatar', 'is_business_account', 'verification_type_id'
                                             ], batch_size=5_000)

    for i, v in dct.items():
        t = Subscriber(login=i, social_id=v['social_id'], social_type_id=3, followers=v['followers'],
                         following=v['following'], contents=v['contents'], name=v['name'], bio=v['bio'],
                         avatar=v['avatar'], is_business_account=v['is_business_account'],
                         verification_type_id=v['verification_type_id'], bloggers=[blogger_id]
                         )
        create.append(t)
    Subscriber.objects.bulk_create(create, batch_size=5_000, ignore_conflicts=True)
    time_print('create subs', len(create))
    subs_new = list(
        Subscriber.objects.filter(social_id__in=list(dct_copy.keys()), social_type_id=3).only('id', 'social_id'))
    mtm_array = []
    for i in subs_new:
        if i.social_id in dct_copy:
            mtm_array.append(SubscriberToBloggerHelpModel(Subscriber_id=i.id, blogger_id=blogger_id))
        avatars.append(
            SubscriberScrappingAvatarInfo(avatar_url=dct_copy[i.social_id]['photo'],
                                          avatar_s3=f"{dct_copy[i.social_id]['pk']}__{i.login}")
        )
    SubscriberToBloggerHelpModel.objects.bulk_create(mtm_array, batch_size=5_000, ignore_conflicts=True)
    time_print('subs mtm', len(mtm_array))
    SubscriberScrappingAvatarInfo.objects.bulk_create(avatars, batch_size=5_000, ignore_conflicts=True)
    time_print('avatars', len(avatars))
