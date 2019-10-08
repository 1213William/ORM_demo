from mysql_singleton import Ms


class Field(object):
	def __init__(self, name, field_type, primary_key, default):
		"""
		:param name: 字段名
		:param field_type: 字段类型
		:param primary_key: 主键
		:param default: 默认值
		"""
		self.name = name
		self.field_type = field_type
		self.primary_key = primary_key
		self.default = default


class StringField(Field):
	def __init__(self, name, field_type="varchar(32)", primary_key=False, default=None):
		"""
		:param name: 字段名
		:param field_type: 字段类型
		:param primary_key: 主键
		:param default: 默认值
		"""
		super().__init__(name, field_type, primary_key, default)


class IntegerField(Field):
	def __init__(self, name, field_type="int", primary_key=False, default=None):
		"""
		:param name: 字段名
		:param field_type: 字段类型
		:param primary_key: 主键
		:param default: 默认值
		"""
		super().__init__(name, field_type, primary_key, default)


class Meta(type):
	def __new__(cls, class_name, class_bases, class_attr):
		"""
		:param class_name: 类名
		:param class_bases: 基类
		:param class_attr: 当前类的名称空间
		:return: 返回__new__对象的实例对象
		"""
		if class_name == 'Model':
			return type.__new__(cls, class_name, class_bases, class_attr)
		table_name = class_attr.get("table_name", class_name)
		primary_key = None
		mappings = {}
		for k, v in class_attr.items():
			if isinstance(v, Field):
				mappings[k] = v
				if v.primary_key:
					if primary_key:
						raise TypeError("一张表只能有一个主键")
					primary_key = v.name
		for k in mappings.keys():
			class_attr.pop(k)
		if not primary_key:
			raise TypeError("一张表必须要有一个主键...")
		class_attr['table_name'] = table_name
		class_attr['primary_key'] = primary_key
		class_attr['mappings'] = mappings
		return type.__new__(cls, class_name, class_bases, class_attr)


class Model(dict, metaclass=Meta):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def __getattr__(self, item):  # 对象点属性的时候会自动走内部的__getattr__
		return self.get(item, "没有主键")

	def __setattr__(self, key, value):
		self[key] = value

	@classmethod
	def select(cls, **kwargs):
		ms = Ms.singleton()
		# 如果没有传入关键字参数那么后面就没有指定查找的条件了
		if not kwargs:
			sql = "select * from %s" % cls.table_name
			res = ms.select(sql)
		else:
			k = list(kwargs.keys())[0]
			v = kwargs.get(k)
			sql = "select * from %s where %s=?" % (cls.table_name, k)  # 如果把那个？改成%s就必须进行传值了，要是不行这样就必须要进行字符串的拼接

			sql = sql.replace('?', '%s')
			res = ms.select(sql, v)
		if res:
			return [cls(**r) for r in res]

	def update(self):
		"""
		update user set name="william" where id=1
		:return:
		"""
		ms = Ms.singleton()
		# 保存主键对应的值
		pr = None
		# 相对应的字段
		field = []
		# 字段对应要修改的值
		values = []
		for k, v in self.mappings.items():
			# 将主键所对应的值赋值给pr
			if v.primary_key:
				pr = getattr(self, v.name, v.default)
			# 如果不是主键，那就是剩下的字段名
			else:
				field.append(v.name + '=?')
				values.append(getattr(self, v.name, v.default))
		sql = "update %s set %s where %s=%s" % (self.table_name, ','.join(field), self.primary_key, pr)
		sql = sql.replace('?', '%s')
		ms.execute(sql, values)

	def save(self):
		"""
		insert into user(name, password) values ("william", 890)
		name、password:键名
		william、890:键值
		:return:
		"""
		ms = Ms.singleton()
		# 保存字段名(除了主键)
		field = []
		# 用来保存字段对应要增加的值
		values = []
		# 有几个字段就需要有几个占位符
		args = []
		for k, v in self.mappings.items():
			# 增加不需要主键所以使用not
			if not v.primary_key:
				field.append(v.name)
				values.append(getattr(self, v.name, v.default))
				args.append('?')
		sql = "insert into %s (%s) values (%s)" % (self.table_name, ','.join(field), ','.join(args))
		# insert into user (name=?, password=?) values (?, ?);
		# 将占位符改成%s，方便之后利用execute进行传值
		sql = sql.replace('?', '%s')
		ms.execute(sql, values)

	def delete(self, **kwargs):
		"""
		delete from user where name="william"

		:return:
		"""
		ms = Ms.singleton()
		if kwargs:
			k = list(kwargs.keys())[0]
			v = kwargs.get(k)  # k:name v:john
			sql = "delete from %s where %s=?" % (self.table_name, k)
			sql = sql.replace('?', '%s')
			ms.execute(sql, v)


class Name(Model):
	table_name = "user"
	id = IntegerField(name="id", primary_key=True)
	name = StringField(name="name")
	password = StringField(name="password")


# 查
res = Name.select()
# 循环遍历删除
for i in res:
	if i.name == '1213William':
		i.delete(name='1213William')
# # print(res)  # 返回出来的是一个列表  要是想取出来就必须要使用索引取值
# res.name = 'jason'
# 改
# res.update()
# print(Name.select(id=3)[0])
# res.name = "john"
# res.password = "123"
# # 增
# res.save()
# res.delete(name='egon')




