from main.models import Blogger
from rest.api.social.services.statistics_service import get_statistic, get_statistic_language


class ApiService:

    @classmethod
    def statistics(cls, blogger: Blogger):
        return get_statistic(blogger, 'ru')

    def statistics_by_date(self):
        pass

    @classmethod
    def statistics_language(cls, blogger: Blogger, language: str):
        return get_statistic(blogger, language)
