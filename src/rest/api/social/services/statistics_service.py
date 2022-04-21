from main.models import Blogger
from rest.api.social.services import blogger_service, posts_service, subsribers_service
from rest.decorators import archive_statistic


@archive_statistic
def get_statistic(blogger: Blogger, language='ru'):
    result = {
        **blogger_service.blogger_service(blogger, language),
        **posts_service.PostsService(blogger, language).posts_service(),
        **subsribers_service.SubscribersService(blogger, language).all()
    }
    return result


# @archive_statistic
def get_statistic_language(blogger: Blogger, language: str):
    return get_statistic(blogger, language)
