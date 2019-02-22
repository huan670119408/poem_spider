import pymysql
from poem_spider.items import PoemItem, PoetItem


class PoemPipeline(object):
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT')
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, self.port, charset='utf8mb4')
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = dict(item)
        keys = ', '.join(data.keys())
        values = ','.join(['%s'] * len(data))
        if isinstance(item, PoemItem):
            del_sql = 'DELETE FROM POEM WHERE TITLE = %s AND DYNASTY = %s AND AUTHOR = %s'
            insert_sql = 'INSERT INTO POEM (%s) VALUES (%s)' % (keys, values)
            self.cursor.execute(del_sql, (data['title'], data['dynasty'], data['author']))
            self.cursor.execute(insert_sql, tuple(data.values()))
            self.db.commit()
        elif isinstance(item, PoetItem):
            del_sql = 'DELETE FROM POET WHERE DYNASTY = %s AND NAME = %s'
            insert_sql = 'INSERT INTO POET (%s) VALUES (%s)' % (keys, values)
            self.cursor.execute(del_sql, (data['dynasty'], data['name']))
            self.cursor.execute(insert_sql, tuple(data.values()))
            self.db.commit()
        return item
