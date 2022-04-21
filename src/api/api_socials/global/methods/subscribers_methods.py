import random

from api.models.extra import Language
from main.models import Subscriber, Blogger
from ..extra import (create_photo_link_extra, date_to_response_date_extra, my_custom_sql_extra,
                     sql_result_none_checking_extra, calculation_of_interest_extra, plus_or_set_extra)

from .. import queries


def subscribers_all(blogger: Blogger):
    return {
        audience_quality.__name__: audience_quality(blogger),
        audience_gender.__name__: audience_gender(blogger),
        audience_cities.__name__: audience_cities(blogger),
        audience_countries.__name__: audience_countries(blogger),
        audience_languages.__name__: audience_languages(blogger),
        audience_activity.__name__: audience_activity(blogger),
    }


def audience_quality(blogger: Blogger):
    queries_accounts = [queries.MASS_FOLLOWERS_PART_QUERY, queries.QUALITY_PART_QUERY,
                        queries.SUSPICIOUS_PART_QUERY,
                        queries.BUSINESSES_PART_QUERY, queries.INFLUENTIAL_PART_QUERY]

    q = queries.AUDIENCE_TEMPLATE_QUERY.format(', '.join(queries_accounts), blogger.id)
    result_of_query = my_custom_sql_extra(q)[0]
    result_of_query = sql_result_none_checking_extra(result_of_query)

    mass_followers, quality_subscribers, suspicious_accounts, businesses, influential = result_of_query

    count_size = mass_followers + quality_subscribers + suspicious_accounts + businesses + influential

    subscribers_count = count_size + 100
    dummy = subscribers_count - count_size

    # Массфоловеры
    mass_followers_count = calculation_of_interest_extra(mass_followers, subscribers_count)

    # Качественная
    quality_subscribers_count = calculation_of_interest_extra(quality_subscribers, subscribers_count)

    # Подозрительная
    suspicious_accounts_count = calculation_of_interest_extra(suspicious_accounts, subscribers_count)

    # Коммерческая
    businesses_count = calculation_of_interest_extra(businesses, subscribers_count)

    # Влиятельные лица
    influential_count = calculation_of_interest_extra(influential, subscribers_count)

    # Пустышки

    dummy_count = calculation_of_interest_extra(dummy, subscribers_count)

    data = {
        "mass_followers": mass_followers_count,
        "quality_subscribers": quality_subscribers_count,
        "businesses": businesses_count,
        "influential": influential_count,
        "suspicious_accounts": suspicious_accounts_count,
        'dummy': dummy_count,
        '__quality_subscribers_count': quality_subscribers + businesses + influential
    }

    return data


def audience_activity(blogger: Blogger):
    banned = random.Random(blogger.dt * 0.1)
    active = blogger.dt - banned
    return dict(banned=calculation_of_interest_extra(banned, blogger.dt),
                active=calculation_of_interest_extra(active, blogger.dt))


def audience_gender(blogger: Blogger):
    result_of_query = my_custom_sql_extra(queries.GENDER_QUERY.format(blogger.id))[0]
    result_of_query = sql_result_none_checking_extra(result_of_query)
    male_, female_, total_ = result_of_query
    male = male_
    female = female_
    not_defined = 10
    total_of_results = male + female + not_defined

    male_count = calculation_of_interest_extra(male, total_of_results)
    female_count = calculation_of_interest_extra(female, total_of_results)
    not_defined_count = calculation_of_interest_extra(not_defined, total_of_results)
    data = {
        "male_count": male_count,
        "female_count": female_count,
        "not_defined_count": not_defined_count
    }

    gender_and_age = my_custom_sql_extra(queries.GENDER_AGE_QUERY.format(blogger.id))
    gender_and_age = sql_result_none_checking_extra(gender_and_age)

    ages_range = ('0_17', '18_24', '25_34', '35_44', '45_54', '>54', 'not_defined_age')
    gender_ages_dict = {}
    for i in ages_range:
        gender_ages_dict[i] = [0, 0, 0, 0]

    for i in gender_and_age:
        if i[0] is None:
            temp_dct = gender_ages_dict[ages_range[6]]
        elif 0 <= i[0] <= 17:
            temp_dct = gender_ages_dict[ages_range[0]]
        elif 18 <= i[0] <= 24:
            temp_dct = gender_ages_dict[ages_range[1]]
        elif 25 <= i[0] <= 34:
            temp_dct = gender_ages_dict[ages_range[2]]
        elif 35 <= i[0] <= 44:
            temp_dct = gender_ages_dict[ages_range[3]]
        elif 45 <= i[0] <= 54:
            temp_dct = gender_ages_dict[ages_range[4]]
        elif i[0] > 54:
            temp_dct = gender_ages_dict[ages_range[5]]
        else:
            continue

        temp_dct[0] += i[1]
        temp_dct[1] += i[2]
        temp_dct[2] += i[3] - (i[1] + i[2])
        temp_dct[3] += i[3]

    global_count = 0
    for i, v in gender_ages_dict.items():
        global_count += (v[0] + v[1])
    male_female_count = 0
    for i, v in gender_ages_dict.items():
        male_female_count += (v[0] + v[1])

        _male_ = calculation_of_interest_extra(v[0], global_count)
        _female_ = calculation_of_interest_extra(v[1], global_count)
        _not_defined_ = calculation_of_interest_extra(v[2], global_count)
        _total_ = v[3]

        data[i] = {"male": _male_,
                   "female": _female_,
                   "not_defined": _not_defined_,
                   "total": _total_}
    return data


def audience_cities(blogger: Blogger):
    cities = my_custom_sql_extra(queries.CITY_QUERY.format(blogger.id))
    data = {}

    cities_size = 0
    for city in cities:
        cities_size += city[1]
    for city in cities:
        if city[0] is None:
            plus_or_set_extra(data, 'Не указан', calculation_of_interest_extra(city[1], cities_size))
        else:
            plus_or_set_extra(data, city[0], calculation_of_interest_extra(city[1], cities_size))
    return data


def audience_countries(blogger: Blogger):
    countries = my_custom_sql_extra(queries.COUNTRY_QUERY.format(blogger.id))
    data = {}
    countries_size = 0
    for country in countries:
        countries_size += country[1]

    for country in countries:
        if country[0] is None:
            plus_or_set_extra(data, 'Не указан', calculation_of_interest_extra(country[1], countries_size))
        else:
            plus_or_set_extra(data, country[0], calculation_of_interest_extra(country[1], countries_size))

    return data


def audience_languages(blogger: Blogger):
    languages_dict = {}
    languages = my_custom_sql_extra(queries.LANGUAGE_QUERY.format(blogger.id))
    data = {}
    languages_size = 0
    for language in languages:
        if language[0] == "":
            continue
        else:
            languages_dict[language[0]] = language[0]

        languages_size += language[1]
    translate_langs = Language.objects.filter(lang__in=list(languages_dict.keys()))
    for l in translate_langs:
        languages_dict[l.lang] = l.name

    for language in languages:
        if language[0] == "":
            continue
        plus_or_set_extra(data, languages_dict[str(language[0])],
                          calculation_of_interest_extra(language[1], languages_size))

    return data
