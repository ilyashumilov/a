import datetime

from dateutil.relativedelta import relativedelta

from api.models import ProceedBlogger


def date_to_front_datetime(date: datetime.datetime):
    try:
        return date.strftime('%Y-%m-%d %H:%M')
    except:
        return None


def date_to_front_date(date: datetime.date):
    try:
        return date.strftime('%Y-%m-%d')
    except:
        return None


def get_dt_from_blogger(blogger: ProceedBlogger):
    dt = blogger.default_total
    if dt is None or dt < 1:
        dt = blogger.subscribers_count
    if dt is None or dt < 1:
        dt = 1

    return dt


def create_line_for_graph(is_min=False):
    if is_min:
        return {'time': date_to_int(datetime.datetime.now()), 'value': 1, 'date': datetime.datetime.now().timestamp()}
    else:
        return {'time': 0, 'value': 1, 'date': 0}


def create_dct_for_graph():
    return {'min': create_line_for_graph(True), 'max': create_line_for_graph(False)}


def date_to_int(date: datetime.datetime):
    return int(date.date().strftime("%Y%m%d"))


def pre_data_for_percent(dct_data: dict, date: datetime.datetime, value):
    t_date = date_to_int(date)
    if dct_data['min']['time'] > t_date:
        dct_data['min']['time'] = t_date
        dct_data['min']['value'] = value
        dct_data['min']['date'] = date.timestamp()

    if dct_data['max']['time'] < t_date:
        dct_data['max']['time'] = t_date
        dct_data['max']['value'] = value
        dct_data['max']['date'] = date.timestamp()


def calculate_percent_new(dct: dict, last, first):
    if last == 0:
        last = 1
    if first == 0:
        first = 1

    t = (last / first) * 100
    t = 1 - t

    return round(t, 2)


def calculate_percent(dct: dict):
    minimum = dct['min']['value']
    maximum = dct['max']['value']
    if minimum == 0:
        minimum = 1

    if minimum < 1 or maximum < 1:
        minimum = int(minimum * 100)
        maximum = int(maximum * 100)
        if minimum == 0:
            minimum = 1
        if maximum == 0:
            maximum = 1

    del dct['min']
    del dct['max']

    try:
        t = (((maximum / minimum) - 1) * 100)
        t = round(t, 2)
        return t
    except Exception as e:
        print(e)
        return 0


def generate_months(min_timestamp: float, max_timestamp: float):
    min_date = datetime.datetime.fromtimestamp(min_timestamp)
    max_date = datetime.datetime.fromtimestamp(max_timestamp)
    cursor_date = min_date
    dates = set()
    while cursor_date <= max_date:
        dates.add(f"{cursor_date.month}.{cursor_date.year}")
        cursor_date += relativedelta(months=1)
    return dates


def add_extra_months(dates: set, values: list, dct: dict):
    for key in dct.keys():
        if key in ('min', 'max'):
            continue
        if key in dates:
            dates.remove(key)
    for i in dates:
        dct[i] = {}
        for k in values:
            dct[i][k] = 0

