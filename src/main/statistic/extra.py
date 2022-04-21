from django.utils import timezone


def plus_to_date_by_months(current_date, months: int):
    """с даты на месяца позже"""
    return current_date - timezone.timedelta(days=30 * months)


def texts_to_words(texts: list):
    words = set()
    for text in texts:
        l = list(map(lambda x: len(x) > 2, list(text)))
        words = words | set(l)
    return list(words)
