from datetime import datetime


def from_line_to_data(a: str):
    a = a.replace('\n', '').strip()

    login_id_index = a.find(':https://')
    login_id_post = a[:login_id_index]
    date_index = a.rfind(':') + 1
    date = a[date_index:]
    temp_str = a[login_id_index + 1:].replace(":" + date, '', 1)
    comments_count_index = temp_str.rfind(':')
    comments_count = temp_str[comments_count_index + 1:]
    temp_str = temp_str[:comments_count_index]
    likes_count_index = temp_str.rfind(':')
    likes_count = temp_str[likes_count_index + 1:]
    temp_str = temp_str[:likes_count_index]

    start = 0
    for k in range(11):
        index_photo = temp_str.find(':', start)
        if temp_str[index_photo + 1] == "/" and temp_str[index_photo + 2] == "/" and temp_str[index_photo - 1] == "s":
            start = index_photo + 1
        else:
            end = index_photo
            break
    photo_url = temp_str[:end]

    # photo_url_index = temp_str.find("https://")
    # photo_url = temp_str[:photo_url_index]
    text = temp_str[end + 1:]

    login_post, id_post = login_id_post.split(":")
    # 20.07.2021_04.35
    # date_as_date = timezone.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    try:
        date_as_date = datetime.strptime(date, '%d.%m.%Y_%H.%M')

    except:
        date_as_date = None

    return login_post, id_post, date_as_date, int(comments_count), int(likes_count), text, photo_url
