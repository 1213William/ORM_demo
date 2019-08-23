import pymysql


class Ms(object):
	_instance = None

	def __init__(self):
		self.conn = pymysql.connect(
			host='127.0.0.1',
			port=3306,
			user='root',
			passwd='123456',
			charset='utf8',
			autocommit=True,
			db='user_info'
		)
		self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

	def close_db(self):
		self.cursor.close()
		self.conn.close()

	def select(self, sql, args=None):
		self.cursor.execute(sql, args)
		res = self.cursor.fetchall()  # 注意一点fetchall拿到的是列表套的字典格式
		return res

	def execute(self, sql, args):
		try:
			self.cursor.execute(sql, args)
		except BaseException as e:
			print(e)

	@classmethod
	def singleton(cls):
		if not cls._instance:
			cls._instance = cls()
		return cls._instance
