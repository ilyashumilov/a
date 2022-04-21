from django.core.management import BaseCommand

# text_to_ad
from django.db.models.functions import Length

from brand_parser.models import Brand, OffsetPostAdvertising
from brand_parser.services import exclude_searchable
from main.models import Post, AdvertisingPost


# curl -X GET "localhost:9200/megacorp/employee/_search?pretty" -H 'Content-Type: application/json' -d' { "query" : { "match_phrase" : { "about" : "rock climbing" } } } '
# https://www.elastic.co/guide/en/elasticsearch/guide/current/_phrase_search.html


class Command(BaseCommand):
    help = "Runs consumer."

    def handle(self, *args, **options):
        print("started ")

        worker()


def extract_words(text: str):
    text = str(text).lower().strip().strip()
    text_split = text.split()
    text_split = list(set(text_split))
    new_text_split = []
    for index, tx in enumerate(text_split):
        t = tx
        if tx.startswith('@'):
            t = tx.replace('@', '')

        if exclude_searchable(t):
            continue
        new_text_split.append(t)

    return new_text_split


def get_brands_from_array(text_array: list, brand_dct: dict):
    all_brands = set()
    for text in text_array:
        for name, value in brand_dct.items():
            if text in name:
                all_brands.add(value)

    return list(all_brands)


def worker():
    offset, created = OffsetPostAdvertising.objects.get_or_create(id=1)
    offset_index = offset.offset
    brand_dct = {}
    for brand in Brand.objects.all():
        brand_dct[brand.name] = brand.id

    while True:
        posts = Post.objects.order_by('id')[offset_index:offset_index + 100]

        for i, post in enumerate(posts):
            brands_ids = get_brands_from_array(extract_words(post.text), brand_dct)
            if len(brands_ids) > 0:
                AdvertisingPost.objects.update_or_create(post=post, brand_ids=brands_ids)
            print(i, len(brands_ids), len(posts), 'offset:', offset_index)
            offset_index += 1

        offset.offset = offset_index
        offset.save()
