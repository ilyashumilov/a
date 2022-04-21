# gan_islam
# rabotaatyrau
from main.statistic.utils import StatisticMethods


def statistic(login: str):
    slice_limit = 18
    sm = StatisticMethods(login)
    LIMIT = 12

    def er12():
        """3. ER (за 12 последних постов)"""

        __likes_count = sm.likes_count(LIMIT)
        __comments_count = sm.comments_count(LIMIT)

        return (((__likes_count + __comments_count) / sm.subscribers_count()) / sm.posts_count()) * 100

    def avg_comments():
        """4. среднее число комментариев"""
        return sm.avg_comments(LIMIT)

    def avg_likes():
        """5. среднее число лайков"""
        return sm.avg_likes(LIMIT)

    def avg_count_posts_by_months():
        """6. частота постов в месяц"""
        return sm.avg_count_of_posts_by_months()

    def coverage():
        """7. прогноз охвата в постах """
        # return (likes_count() + comments_count()) / sub_query.count()
        return (sm.likes_count() + sm.comments_count()) / sm.subscribers_count()

    def involvement():
        """10. вовлеченность аудитории """
        return ((sm.avg_likes() + sm.avg_comments()) / sm.subscribers_count()) * 100

    def posts_likes_sum():
        """15. количество лайков"""
        return sm.likes_count()

    def posts_comments_sum():
        """16. количество комментариев"""
        return sm.comments_count()

    def hashtags():
        """17. теги у блогера """
        return sm.hashtags_from_posts()

    def brand_affinity():
        # todo бренды подключить
        """18. бренд аффинитивность"""
        return sm.brand_affinity()

    """extra features"""

    def count_advertising_posts():
        """1. частота рекламных постов в аккаунте (в месяц)"""
        return sm.count_advertising_posts()

    def five_last_advertisers():
        """4. 5 последних рекламодаталей"""
        return sm.five_last_advertisers()

    def the_most_popular_post():
        """5. самый крутой рекламный пост в аккаунте блогера"""
        return sm.the_most_popular_post()

    def popular_day():
        """6. в какой день и в какое время публикации набирают наибольший охват"""
        return sm.popular_day_and_hour()

    def relevant_bloggers():
        """2. вовлечение"""
        return sm.relevant_bloggers()

    def audience_quality():
        """11. качество аудитории"""
        return sm.audience_quality()

    def audience_count():
        """16. количество качественной аудитории"""
        return sm.audience_count()

    def advertisement_price():
        """Но в качестве киллер фичи хотелось бы иметь возможность забить цены на блогеров, и найти оптимальный микс/лучшее число контактов с аудиторией."""
        return sm.advertisement_price()

    try:
        return {
            er12.__name__: {
                'data': er12(),
                'description': er12.__doc__
            },
            avg_comments.__name__: {
                'data': avg_comments(),
                'description': avg_comments.__doc__
            },
            avg_likes.__name__: {
                'data': avg_likes(),
                'description': avg_likes.__doc__
            },
            avg_count_posts_by_months.__name__: {
                'data': avg_count_posts_by_months(),
                'description': avg_count_posts_by_months.__doc__
            },
            coverage.__name__: {
                'data': coverage(),
                'description': coverage.__doc__
            },
            involvement.__name__: {
                'data': involvement(),
                'description': involvement.__doc__
            },
            posts_likes_sum.__name__: {
                'data': posts_likes_sum(),
                'description': posts_likes_sum.__doc__
            },
            posts_comments_sum.__name__: {
                'data': posts_comments_sum(),
                'description': posts_comments_sum.__doc__
            },
            hashtags.__name__: {
                'data': hashtags(),
                'description': hashtags.__doc__
            },
            brand_affinity.__name__: {
                'data': brand_affinity(),
                'description': brand_affinity.__doc__
            },
            count_advertising_posts.__name__: {
                'data': count_advertising_posts(),
                'description': count_advertising_posts.__doc__
            },
            five_last_advertisers.__name__: {
                'data': five_last_advertisers(),
                'description': five_last_advertisers.__doc__
            },
            the_most_popular_post.__name__: {
                'data': the_most_popular_post(),
                'description': the_most_popular_post.__doc__
            },
            popular_day.__name__: {
                'data': popular_day(),
                'description': popular_day.__doc__
            },
            relevant_bloggers.__name__: {
                'data': relevant_bloggers(),
                'description': relevant_bloggers.__doc__
            },
            audience_quality.__name__: {
                'data': audience_quality(),
                'description': audience_quality.__doc__
            },
            audience_count.__name__: {
                'data': audience_count(),
                'description': audience_count.__doc__
            },
            advertisement_price.__name__: {
                'data': advertisement_price(),
                'description': advertisement_price.__doc__
            },
        }
    except Exception as e:
        print(e)
        return {"message": 'Блогер еще не готов'}
