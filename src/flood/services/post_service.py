from django.utils import timezone

from flood.services.global_service import url_normalize


def extract_post_from_line(a: str):
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


        except Exception as e:
            print(e)

    return dct
