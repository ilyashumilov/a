from django.db.models import Q

from main.models import Blogger


def metrics():
    default_total = all_methods('default_total')
    post_default_count = all_methods('post_default_count')

    return dict(default_total=default_total, post_default_count=post_default_count)


def all_methods(field: str):
    max, min = get_max_and_min(field)
    steps = generate_steps(max, min)
    steps_type = ('big', 'big', 'small', 'small', 'small')
    for i, v in enumerate(steps):
        steps[i] = round_step(v, steps_type[i])
    return steps


def get_max_and_min(field: str):
    dct = {f'{field}__gt': 0}
    q = (Q(**dct) & Q(file_from_info__overlap=['Топ']))
    max_blogger = Blogger.objects.filter(q).order_by(f'-{field}').only(field).first()
    max = getattr(max_blogger, field)
    min_blogger = Blogger.objects.filter(q).order_by(f'{field}').only(field).first()
    min = getattr(min_blogger, field)

    return max, min


def generate_steps(max: int, min: int) -> list:
    t = max - min
    steps_percents = [0.75, 0.5, 0.25]
    steps = [max]
    for i in steps_percents:
        steps.append(int(t * i))
    steps.append(min)
    print('steps', steps)
    return steps


def round_step(value: int, round_type: str):
    value_ = str(value)
    t1 = int(value_[0])
    t2 = value_[1:]
    try:
        t2_ = int(t2)
    except ValueError:
        t2_ = 5

    delta = int('5' + '0' * (len(t2) - 1))
    if round_type == 'big':
        if t2_ <= delta:
            t3 = f'{t1}{delta}'
        else:
            t1 += 1
            t3 = f'{t1}' + '0' * (len(t2))
    else:
        if t2_ >= delta:
            t3 = f'{t1}{delta}'
        else:
            t3 = f'{t1}' + '0' * (len(t2))
    return add_suffix(int(t3))


def add_suffix(value: int):
    if 1_000_000 <= value:
        value_ = str(value // 1_000_000)
        value_ = f'{value_}M'
    elif 1_000 <= value < 1_000_000:
        value_ = str(value // 1_000)
        value_ = f'{value_}K'
    elif 100 <= value < 1_000:
        value_ = str(value // 100)
        value_ = f'0.{int(value_)}K'
    else:
        value_ = str(value)
    return {value_: value}
