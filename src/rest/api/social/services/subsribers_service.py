import itertools
from collections import Counter

from main.models import Blogger
from rest.api.social.methods import util_methods, queries, tags_methods
from rest.api.social.methods.text_methods import rm_all_not_symb_in_text
from rest.api.social.services.language_controller import LanguageController
from rest.decorators import cacheable_db_data, timeit


class SubscribersService:
    def __init__(self, blogger: Blogger, language='ru'):
        self.blogger = blogger
        self.language = language

    def audience_quality(self):
        queries_accounts = [queries.MASS_FOLLOWERS_PART_QUERY, queries.QUALITY_PART_QUERY,
                            queries.SUSPICIOUS_PART_QUERY,
                            queries.BUSINESSES_PART_QUERY, queries.INFLUENTIAL_PART_QUERY]

        q = queries.AUDIENCE_TEMPLATE_QUERY.format(', '.join(queries_accounts), self.blogger.id)
        result_of_query = util_methods.my_custom_sql(q)[0]
        result_of_query = util_methods.sql_result_none_checking(result_of_query)

        mass_followers, quality_subscribers, suspicious_accounts, businesses, influential = result_of_query

        count_size = mass_followers + quality_subscribers + suspicious_accounts + businesses + influential

        subscribers_count = count_size + 100
        dummy = subscribers_count - count_size

        # Массфоловеры
        mass_followers_count = util_methods.calculation_of_interest(mass_followers, subscribers_count)

        # Качественная
        quality_subscribers_count = util_methods.calculation_of_interest(quality_subscribers, subscribers_count)

        # Подозрительная
        suspicious_accounts_count = util_methods.calculation_of_interest(suspicious_accounts, subscribers_count)

        # Коммерческая
        businesses_count = util_methods.calculation_of_interest(businesses, subscribers_count)

        # Влиятельные лица
        influential_count = util_methods.calculation_of_interest(influential, subscribers_count)

        # Пустышки

        dummy_count = util_methods.calculation_of_interest(dummy, subscribers_count)

        data = {
            "mass_followers": mass_followers_count,
            "quality_subscribers": quality_subscribers_count,
            "businesses": businesses_count,
            "influential": influential_count,
            "suspicious_accounts": suspicious_accounts_count,
            'dummy': dummy_count,
            '__quality_subscribers_count': int(self.blogger.default_total * 0.2)
        }

        return data

    def audience_activity(self):
        count = self.blogger.dt
        banned = int(count * 0.1)
        active = count - banned
        return dict(banned=util_methods.calculation_of_interest(banned, count),
                    active=util_methods.calculation_of_interest(active, count))

    def audience_gender(self):

        result_of_query = util_methods.my_custom_sql(queries.GENDER_QUERY.format(self.blogger.id))[0]
        result_of_query = util_methods.sql_result_none_checking(result_of_query)
        male_, female_, total_ = result_of_query
        male = male_
        female = female_
        not_defined = 10
        total_of_results = male + female + not_defined

        male_count = util_methods.calculation_of_interest(male, total_of_results)
        female_count = util_methods.calculation_of_interest(female, total_of_results)
        not_defined_count = util_methods.calculation_of_interest(not_defined, total_of_results)
        data = {
            "male_count": male_count,
            "female_count": female_count,
            "not_defined_count": not_defined_count
        }

        gender_and_age = util_methods.my_custom_sql(queries.GENDER_AGE_QUERY.format(self.blogger.id))
        gender_and_age = util_methods.sql_result_none_checking(gender_and_age)

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

            _male_ = util_methods.calculation_of_interest(v[0], global_count)
            _female_ = util_methods.calculation_of_interest(v[1], global_count)
            _not_defined_ = util_methods.calculation_of_interest(v[2], global_count)
            _total_ = v[3]

            data[i] = {"male": _male_,
                       "female": _female_,
                       "not_defined": _not_defined_,
                       "total": _total_}
        return data

    def audience_cities(self):
        q = queries.lang_query_replace(queries.CITY_QUERY.format(self.blogger.id), self.language)
        cities = util_methods.my_custom_sql(q)
        data = {}

        cities_size = 0
        for city in cities:
            cities_size += city[1]
        for city in cities:
            if city[0] is None:
                util_methods.plus_or_set(data, LanguageController.get_not_defined(self.language),
                                         util_methods.calculation_of_interest(city[1], cities_size))
            else:
                util_methods.plus_or_set(data, city[0], util_methods.calculation_of_interest(city[1], cities_size))
        return data

    def audience_countries(self):
        q = queries.lang_query_replace(queries.COUNTRY_QUERY.format(self.blogger.id), self.language)
        countries = util_methods.my_custom_sql(q)
        data = {}
        countries_size = 0
        for country in countries:
            countries_size += country[1]

        for country in countries:
            if country[0] is None:
                util_methods.plus_or_set(data, LanguageController.get_not_defined(self.language),
                                         util_methods.calculation_of_interest(country[1], countries_size))
            else:
                util_methods.plus_or_set(data, country[0],
                                         util_methods.calculation_of_interest(country[1], countries_size))

        return data

    def audience_languages(self):
        q = queries.lang_query_replace(queries.LANGUAGE_QUERY.format(self.blogger.id), self.language)
        languages = util_methods.my_custom_sql(q)
        data = {}
        languages_size = 0
        for language in languages:
            if language[0] == "":
                continue
            languages_size += language[1]

        for language in languages:
            if language[0] == "":
                continue
            util_methods.plus_or_set(data, language[0],
                                     util_methods.calculation_of_interest(language[1], languages_size))

        return data

    def words_in_bio_subscribers(self):
        bios = util_methods.my_custom_sql(queries.BIO_QUERY.format(self.blogger.id))
        dct = {}

        for bio in bios:

            bio: str = str(bio[0])
            bio_ = rm_all_not_symb_in_text(bio.lower())
            # bio_ = ''.join(list(filter(lambda x: len(x) > 3, list(bio_))))

            text_dct = Counter(tags_methods.tags_extract_v2(bio_))

            for key, value in text_dct.items():
                if len(key) <= 3:
                    continue
                if key not in dct:
                    dct[key] = value
                else:
                    dct[key] += value

        new_dct = {}
        for i, v in dct.items():
            if v > 1:
                new_dct[i] = v

        new_dct = dict(sorted(new_dct.items(), key=lambda item: item[1], reverse=True))
        return dict(itertools.islice(new_dct.items(), 50))

    @timeit
    @cacheable_db_data
    def all(self):
        quality = self.audience_quality()
        return {
            self.audience_quality.__name__: quality,
            self.audience_gender.__name__: self.audience_gender(),
            self.audience_cities.__name__: self.audience_cities(),
            self.audience_countries.__name__: self.audience_countries(),
            self.audience_languages.__name__: self.audience_languages(),
            self.audience_activity.__name__: self.audience_activity(),
            "words_in_bio": self.words_in_bio_subscribers(),
            'audience_count': quality['__quality_subscribers_count']
        }
