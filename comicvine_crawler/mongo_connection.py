from pymongo import MongoClient


class Connect(object):
    @staticmethod
    def get_connection(url):
        return MongoClient(url)
