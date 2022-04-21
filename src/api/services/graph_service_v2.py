import time
from typing import List

from django.db.models import Q, QuerySet, Count

from api.data import queries
from api.models.extra import Language
from api.services.methods import timeit, sql_result_none_checking
from main.models import Subscriber, Blogger
from math import ceil
from django.db import connection

from parsing.ParsingModules.ParsingModule import time_print


def my_custom_sql(sql_query):
    with connection.cursor() as cursor:
        cursor.execute(sql_query)
        rows = cursor.fetchall()

    return rows


def plus_or_set(dct, name, value):
    if name not in dct:
        dct[name] = 0
    dct[name] += value


class Graph(object):

    def __init__(self, blogger: Blogger, subscribers: QuerySet[Subscriber]):
        self.blogger_id = blogger.id
        self.count = len(subscribers)

        # self.count = blogger.default_total
        # self.count_usually = self.subscribers.filter(~Q(following=None)).count()
        # self.detail_count = self.count_usually - self.subscribers.filter(Q(gender_id=1) | Q(gender_id=2)).count()
        # # blogger.dt
        # self.coeff = self.count // self.count_usually

    def calculation_of_interest(self, num, count=None, one_hundred=True):
        t_num = num
        if count is None:
            count = self.count

        if count != 0:
            if one_hundred:
                num = num / count * 100
            else:
                num = num / count

        if 1 > num:
            num = ceil(num * 100) / 100.0

        if 0.1 > num > 0:
            num = 0.1

        return round(num, 2)

    @timeit
    def audience_quality(self):
        queries_accounts = [queries.MASS_FOLLOWERS_PART_QUERY, queries.QUALITY_PART_QUERY,
                            queries.SUSPICIOUS_PART_QUERY,
                            queries.BUSINESSES_PART_QUERY, queries.INFLUENTIAL_PART_QUERY]

        q = queries.AUDIENCE_TEMPLATE_QUERY.format(', '.join(queries_accounts), self.blogger_id)
        result_of_query = my_custom_sql(q)[0]
        result_of_query = sql_result_none_checking(result_of_query)

        mass_followers, quality_subscribers, suspicious_accounts, businesses, influential = result_of_query

        # mass_followers *= self.coeff
        # quality_subscribers *= self.coeff
        # suspicious_accounts *= self.coeff
        # businesses *= self.coeff
        # influential *= self.coeff
        count_size = mass_followers + quality_subscribers + suspicious_accounts + businesses + influential

        subscribers_count = count_size + 100
        dummy = subscribers_count - count_size

        # Массфоловеры
        mass_followers_count = self.calculation_of_interest(mass_followers, subscribers_count)

        # Качественная
        quality_subscribers_count = self.calculation_of_interest(quality_subscribers, subscribers_count)

        # Подозрительная
        suspicious_accounts_count = self.calculation_of_interest(suspicious_accounts, subscribers_count)

        # Коммерческая
        businesses_count = self.calculation_of_interest(businesses, subscribers_count)

        # Влиятельные лица
        influential_count = self.calculation_of_interest(influential, subscribers_count)

        # Пустышки

        dummy_count = self.calculation_of_interest(dummy, subscribers_count)

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

    @timeit
    def audience_activity(self):
        banned = int(self.count * 0.1)
        # active = self.count_usually - banned
        active = self.count - banned
        return dict(banned=self.calculation_of_interest(banned), active=self.calculation_of_interest(active))

    @timeit
    def audience_gender(self):

        result_of_query = my_custom_sql(queries.GENDER_QUERY.format(self.blogger_id))[0]
        result_of_query = sql_result_none_checking(result_of_query)
        male_, female_, total_ = result_of_query
        male = male_
        female = female_
        not_defined = 10
        total_of_results = male + female + not_defined

        male_count = self.calculation_of_interest(male, total_of_results)
        female_count = self.calculation_of_interest(female, total_of_results)
        not_defined_count = self.calculation_of_interest(not_defined, total_of_results)
        data = {
            "male_count": male_count,
            "female_count": female_count,
            "not_defined_count": not_defined_count
        }

        gender_and_age = my_custom_sql(queries.GENDER_AGE_QUERY.format(self.blogger_id))
        gender_and_age = sql_result_none_checking(gender_and_age)

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

            _male_ = self.calculation_of_interest(v[0], global_count)
            _female_ = self.calculation_of_interest(v[1], global_count)
            _not_defined_ = self.calculation_of_interest(v[2], global_count)
            _total_ = v[3]

            data[i] = {"male": _male_,
                       "female": _female_,
                       "not_defined": _not_defined_,
                       "total": _total_}
        return data

    @timeit
    def audience_cities(self):
        cities = my_custom_sql(queries.CITY_QUERY.format(self.blogger_id))
        data = {}

        cities_size = 0
        for city in cities:
            cities_size += city[1]
        for city in cities:
            if city[0] is None:
                plus_or_set(data, 'Не указаны', self.calculation_of_interest(city[1], cities_size))
            else:
                plus_or_set(data, city[0], self.calculation_of_interest(city[1], cities_size))
        return data

    @timeit
    def audience_countries(self):
        countries = my_custom_sql(queries.COUNTRY_QUERY.format(self.blogger_id))
        data = {}
        countries_size = 0
        for country in countries:
            countries_size += country[1]

        for country in countries:
            if country[0] is None:
                plus_or_set(data, 'Не указаны', self.calculation_of_interest(country[1], countries_size))
            else:
                plus_or_set(data, country[0], self.calculation_of_interest(country[1], countries_size))

        return data

    @timeit
    def audience_languages(self):
        languages_dict = {}
        languages = my_custom_sql(queries.LANGUAGE_QUERY.format(self.blogger_id))
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
            plus_or_set(data, languages_dict[str(language[0])],
                        self.calculation_of_interest(language[1], languages_size))
            # data[languages_dict[str(language[0])]] = self.calculation_of_interest(language[1], languages_size)

        return data

    def all(self):
        return {
            self.audience_quality.__name__: self.audience_quality(),
            self.audience_gender.__name__: self.audience_gender(),
            self.audience_cities.__name__: self.audience_cities(),
            self.audience_countries.__name__: self.audience_countries(),
            self.audience_languages.__name__: self.audience_languages(),
            self.audience_activity.__name__: self.audience_activity(),
        }
