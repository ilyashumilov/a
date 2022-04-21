import multiprocessing
import os

from dotenv import find_dotenv, load_dotenv

from parsing.AsyncParsingNew import utils

load_dotenv(find_dotenv())

db = {
    "USER": os.environ.get("DB_USER"),
    "PASSWORD": os.environ.get('DB_PASSWORD'),
    "HOST": os.environ.get('DB_HOST'),
    "NAME": os.environ.get('DB_NAME')
}

class MTestMulti:
    def __init__(self):
        self.counter = 0
        self.loop = utils.create_loop()
        self.pool = self.loop.run_until_complete(utils.create_pool(db))

    def coro(self):
        with multiprocessing.Pool(2) as p:
            p.map(self.p, [1])

    def p(self,q):
        print(self.pool)
        print(self.counter)


if __name__ == '__main__':
    MTestMulti().coro()
