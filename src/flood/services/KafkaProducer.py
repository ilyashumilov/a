import json

from django.conf import settings
from kafka import KafkaProducer
from aiokafka import AIOKafkaProducer


def json_serializer(data):
    return json.dumps(data).encode('utf-8')


class TopicChooser:
    topics = ("photos_s3", "videos_s3")

    @classmethod
    def choose(cls, url: str):
        if '.mp4' in url:
            return cls.topics[1]
        else:
            return cls.topics[0]


class AsyncKafkaProducer:
    producer = AIOKafkaProducer(bootstrap_servers=f'{settings.KAFKA_IP}:9092', value_serializer=json_serializer)

    @classmethod
    async def push(cls, data: dict):
        await cls.producer.start()
        try:
            # Produce message
            for url, photo_s3 in data.items():
                topic = TopicChooser.choose(url)
                await cls.producer.send_and_wait(topic, dict(url=url, photo_s3=photo_s3))
        finally:
            # Wait for all pending messages to be delivered or expire.
            await cls.producer.stop()


class KafkaProducerPhotoVideo:
    producer = KafkaProducer(bootstrap_servers=[f'{settings.KAFKA_IP}:9092'],
                             value_serializer=json_serializer)

    @classmethod
    def send_url(cls, url: str, photo_s3: str):
        try:
            topic = TopicChooser.choose(url)
            data = dict(url=url, photo_s3=photo_s3)
            cls.producer.send(topic, data)
        except Exception as e:
            print(e)

    @classmethod
    def push_dct(cls, photos_videos: dict):
        for url, photo_s3 in photos_videos.items():
            cls.send_url(url, photo_s3)
        cls.flush()

    @classmethod
    def flush(cls, timeout=60*5):
        cls.producer.flush(timeout=timeout)
