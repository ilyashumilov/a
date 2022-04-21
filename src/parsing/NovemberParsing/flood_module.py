import asyncio
import time

import asyncpg
from asyncpg import Connection
from django.conf import settings

from parsing.AsyncParsingNew import utils
from parsing.AsyncParsingNew.utils import time_print
from tortoise_base import db_init


class FloodModule(object):
    def __init__(self):

        self.batch_size = 50_000
        self.T_N = 10_000

