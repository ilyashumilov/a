import requests
from django.utils import timezone
from django.utils.timezone import make_aware


def url_normalize(link: str):
    return link.replace(r'\u0026', '&')


def extract_post_from_line(line: str):
    line = line.replace('\n', ' ').strip().replace('  ', ' ')
    post_login_index = line.find(':')
    post_id_index = line.find(':', post_login_index + 1)

    post_login = line[:post_login_index]
    post_id = line[post_login_index + 1:post_id_index]

    line = line[post_id_index + 1:]
    __photo_offset = len('https:')
    photo_end_index = min((line.find(',', __photo_offset), line.find(':', __photo_offset)))
    first_photo = line[:photo_end_index]
    try:
        __offset = 0
        for i in range(11):
            __index = line.find(':', __offset)
            if line[__index - 5:].startswith('https:'):
                __offset = __index + 1
            else:
                last_photo = line[__offset - __photo_offset:]

                last_photo = last_photo[:last_photo.index(':', __photo_offset)]
                first_photo=last_photo

        line = line[line.find(':', __offset + __photo_offset) + 1:]

    except Exception as e:
        print(e)

    #     2052226:53134:0:31.05.2018_23.03
    #     likes:comments:views:date
    temp_index = line.rfind(':')
    __date = line[temp_index + 1:]
    line = line[:temp_index]
    temp_index = line.rfind(':')
    __comments_1 = line[temp_index + 1:]
    line = line[:temp_index]
    temp_index = line.rfind(':')
    __comments_2 = line[temp_index + 1:]
    line = line[:temp_index]
    try:
        temp_index = line.rfind(':')
        __comments_3 = int(line[temp_index + 1:])
        likes = __comments_3
        comments = int(__comments_2)
        views = int(__comments_1)
    except:
        likes = int(__comments_2)
        comments = int(__comments_1)
        views = 0

    text = line[:temp_index]

    try:
        date_as_date = timezone.datetime.strptime(__date, '%d.%m.%Y_%H.%M')
    except Exception as e:
        date_as_date = None

    return post_login, post_id, date_as_date, comments, likes, text, first_photo, views


def extract_post_from_line_old(a: str):
    a = a.replace('\n', '').strip()

    login_id_index = a.find(':https://')
    login_id_post = a[:login_id_index]
    date_index = a.rfind(':') + 1
    date = a[date_index:]
    temp_str = a[login_id_index + 1:].replace(":" + date, '', 1)

    comments_count_index = temp_str.rfind(':')
    comments_count = temp_str[comments_count_index + 1:]
    temp_str = temp_str[:comments_count_index]
    # 91762:6422:0:22.02.2022_15.19
    likes_count_index = temp_str.rfind(':')
    likes_count = temp_str[likes_count_index + 1:]
    temp_str = temp_str[:likes_count_index]

    # просмотры
    try:
        likes_count_index_v2 = temp_str.rfind(':')
        likes_count_v2 = temp_str[likes_count_index_v2 + 1:]
        likes_count_v2 = int(likes_count_v2)
        views_count, comments_count = comments_count, likes_count
        likes_count = likes_count_v2
        temp_str = temp_str[:likes_count_index_v2]

    except:
        views_count = 0
        pass

    start = 0
    for k in range(11):
        index_photo = temp_str.find(':', start)
        if temp_str[index_photo + 1] == "/" and temp_str[index_photo + 2] == "/" and temp_str[index_photo - 1] == "s":
            start = index_photo + 1
        else:
            end = index_photo
            break
    photo_url = temp_str[:end]
    all_photos = []
    urls_lines = a.split('https:')[1:]
    urls_lines[-1] = urls_lines[-1].split(':')[0]
    for u, _ in enumerate(urls_lines):
        urls_lines[u] = 'https:' + urls_lines[u].replace(',', '')

    # photo_url_index = temp_str.find("https://")
    # photo_url = temp_str[:photo_url_index]
    text = temp_str[end + 1:]

    login_post, id_post = login_id_post.split(":")
    # 20.07.2021_04.35
    # date_as_date = timezone.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    try:
        date_as_date = timezone.datetime.strptime(date, '%d.%m.%Y_%H.%M')
        # date_as_date = make_aware(timezone.datetime.strptime(date, '%d.%m.%Y_%H.%M'))


    except Exception as e:
        print('date', e)
        date_as_date = None

    return login_post, id_post, date_as_date, int(comments_count), int(likes_count), text, urls_lines[0], int(
        views_count)


def extract_all_posts(text: str):
    data = text
    post_dublicates = set()
    dct = {}
    s = []
    __login_post = ""
    for line in data.split('\n'):
        ln = line.strip().replace('\n', '')
        try:
            if ln.find(':https://instagram') > 0:
                s.clear()
            s.append(ln)

            final_line = ' '.join(s)
            try:
                login_post, id_post, date, comments_count, \
                likes_count, text, photo, views_count = extract_post_from_line(final_line)
                s.clear()

            except Exception as e:
                print(e)
                continue
                pass
            if id_post in post_dublicates:
                continue
            else:
                post_dublicates.add(id_post)

            dct[id_post] = [id_post, login_post, url_normalize(photo), text,
                            likes_count, comments_count, date, views_count]
            __login_post = login_post

        except Exception as e:
            print(e)

    return dct, __login_post
