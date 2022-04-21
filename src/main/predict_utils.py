import asyncio
import random
from collections import namedtuple
from datetime import datetime, timedelta
from operator import itemgetter


def get_date_index(worksheet):
    today = datetime.now().strftime('%d.%m.%Y')
    return worksheet.col_values(col=2).index(today)


def smooth(iq_data, alpha=1, today=None):
    """Perform exponential smoothing with factor `alpha`.

    Time period is a day.
    Each time period the value of `iq` drops `alpha` times.
    The most recent data is the most valuable one.
    """
    assert 0 < alpha <= 1

    if alpha == 1:  # no smoothing
        return sum(map(itemgetter(1), iq_data))

    if today is None:
        today = max(map(itemgetter(0), iq_data))

    return sum(alpha ** ((today - date).days) * iq for date, iq in iq_data)


IQData = namedtuple("IQData", "date iq")


def gen_secuence(n):
    a = 500
    t = []
    for i in range(n):
        a += random.randint(1, 100)
        t.append(a)
    print(t)
    return t


def dt(i, n):
    return datetime.now() - timedelta(days=n - i)


# счет с нуля если
def update_cell_on_index(index, col, text, worksheet):
    print(text)
    index += 1
    col += 1
    a = worksheet.cell(index, col)
    print(a)
    worksheet.update_cell(index, col, text)


def get_predict(arr):
    IQ = arr
    days = [dt(i, len(arr)) for i in range(len(arr))]
    iqdata = list(map(IQData, days, IQ))
    return smooth(iqdata, alpha=0.1)


def predict(col, worksheet):
    values = [i.replace(r'\xa0', '').replace(" ", '').replace(' ', '') for i in worksheet.col_values(col)[1:]]

    return int(get_predict(list(map(int, values))))
