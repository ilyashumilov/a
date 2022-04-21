from intercalation.base_modules.BaseFloodModel import BaseFloodModel
from main.models import Subscriber


def update_fields(exist_subscriber: Subscriber, new_subscriber: Subscriber):
    change = BaseFloodModel.change
    change(exist_subscriber, new_subscriber, 'login')
    change(exist_subscriber, new_subscriber, 'name')
    change(exist_subscriber, new_subscriber, 'followers')
    change(exist_subscriber, new_subscriber, 'following')
    change(exist_subscriber, new_subscriber, 'contents')
    change(exist_subscriber, new_subscriber, 'status_id')
    change(exist_subscriber, new_subscriber, 'verification_type_id')
    change(exist_subscriber, new_subscriber, 'avatar')
    change(exist_subscriber, new_subscriber, 'bio')
    change(exist_subscriber, new_subscriber, 'category_id')
    change(exist_subscriber, new_subscriber, 'external_link')
    change(exist_subscriber, new_subscriber, 'address_id')
    change(exist_subscriber, new_subscriber, 'language_id')
    change(exist_subscriber, new_subscriber, 'is_business_account')
    change(exist_subscriber, new_subscriber, 'email')
    change(exist_subscriber, new_subscriber, 'phone_number')


def get_fields():
    return ['login', 'name', 'followers', 'following', 'contents',
            'status_id', 'verification_type_id', 'avatar', 'bio', 'category_id',
            'external_link', 'address_id', 'language_id', 'is_business_account',
            'email', 'phone_number']


def get_fields_detail():
    data = ['bloggers']
    data.extend(get_fields())
    return data
