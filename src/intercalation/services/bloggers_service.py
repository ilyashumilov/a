from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from main.models import Blogger


def update_fields(exist_blogger: Blogger, new_blogger: Blogger):
    change = BaseFloodModel.change
    change(exist_blogger, new_blogger, 'login')
    change(exist_blogger, new_blogger, 'name')
    change(exist_blogger, new_blogger, 'default_total')
    change(exist_blogger, new_blogger, 'following')
    change(exist_blogger, new_blogger, 'post_default_count')
    change(exist_blogger, new_blogger, 'status_id')
    change(exist_blogger, new_blogger, 'verification_type_id')
    change(exist_blogger, new_blogger, 'avatar')
    change(exist_blogger, new_blogger, 'bio')
    change(exist_blogger, new_blogger, 'category_id')
    change(exist_blogger, new_blogger, 'external_link')
    change(exist_blogger, new_blogger, 'address_id')
    change(exist_blogger, new_blogger, 'language_id')
    change(exist_blogger, new_blogger, 'is_business_account')
    change(exist_blogger, new_blogger, 'email')
    change(exist_blogger, new_blogger, 'phone_number')


def get_fields():
    return ['login', 'name', 'default_total', 'following', 'post_default_count',
            'status_id', 'verification_type_id', 'avatar', 'bio', 'category_id',
            'external_link', 'address_id', 'language_id', 'is_business_account',
            'email', 'phone_number', 'is_advertiser']
