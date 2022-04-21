from main.models import Post
from rest.api.social.methods import util_methods


def post_to_dict(post: Post):

    photo_url = util_methods.create_photo_link(post.photos_url)

    return {'id': post.id,
            'post_id': post.post_id,
            'post_login': post.post_login,
            'post_url': f"https://www.instagram.com/p/{post.post_id}/",
            'photos_url': [photo_url],
            'text': post.text,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'time': post.date.strftime('%H:%M'),
            'date': post.date.strftime('%Y-%m-%d'),
            "__sum_likes_comments": post.likes_count + post.comments_count
            }
