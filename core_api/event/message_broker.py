from extensions.rabbitmq import AsyncRabbitMQProducer, AsyncRabbitMQConsumer
from messaging_tools import EventBus, Message

from settings import config

async def produce_message(message):

    async with AsyncRabbitMQProducer(url=config.rabbitmq_url) as producer:
        await producer.publish('events', message.model_dump_json(by_alias=True))