#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

#编写一个orm框架来处理数据库的增删改查
import asyncio, logging
import aiomysql

def log(sql, args=()): #打印日志函数
	logging.info('SQL:%s' % sql)

#创建连接池
async def create_pool(loop, **kw):
	logging.info('create database connection pool……')
	global __pool #全局变量来存储连接池
	__pool = await aiomysql.create_pool(
			host=kw.get('host', 'localhost'),
	        port=kw.get('port', 3306),
	        user=kw['user'],
	        password=kw['password'],
	        db=kw['db'],
	        charset=kw.get('charset', 'utf8'),
	        autocommit=kw.get('autocommit', True),
	        maxsize=kw.get('maxsize', 10),
	        minsize=kw.get('minsize', 1),
	        loop=loop
		) 

#查询数据库
async def select(sql, args, size=None): #传入带参的sql,防止sql注入
	log(sql, args)
	async with __pool.get() as conn: #通过连接池创建一个连接
		async with conn.cursor(aiomysql.DictCursor) as cur: #创建游标
			await cur.execute(sql.replace('?', '%s'), args or ()) #执行sql语句
			if size:
				rs = await cur.fetchmany(size)
			else:
				rs = await cur.fetchall()  #拿到查询结果
		logging.info('rows returned: %s' % len(rs))
		return rs #返回查询结果
#如果传入size参数，就通过fetchmany()获取最多指定数量的记录，否则，通过fetchall()获取所有记录。

#插入、更新、删除
async def execute(sql, args, autocommit=True):
	log(sql)
	async with __pool.get() as conn:#连接数据库
		if not autocommit:
			await conn.begin()
		try:
			async with conn.cursor(aiomysql.DictCursor) as cur:
				print(args)
				await cur.execute(sql.replace('?', '%s'), args)
				affected = cur.rowcount #返回结果数，比如插入了1行
				logging.info('affected------: %s' % affected)
			if not autocommit:
				await conn.commit()
		except BaseException as e:
			if not autocommit:
				await conn.rollback()#有插入失败，数据库回滚到原样
			raise
		return affected

#编写ROM,把数据库表和python类的对象对应起来

def create_args_string(num):
	L = []
	for n in range(num):
		L.append('?')
	return ', '.join(L)


class Field(object):
	def __init__(self, name, column_type, primary_key, default):
		self.name = name
		self.column_type = column_type
		self.primary_key = primary_key
		self.default = default

	def __str__(self):
		return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
	def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
		super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):
	def __init__(self, name=None, default=False):
		super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
	def __init__(self, name=None, primary_key=False, default=0):
		super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):
	def __init__(self, name=None, primary_key=False, default=0.0):
		super().__init__(name, 'real', primary_key, default)

class TextField(Field):
	def __init__(self, name=None, default=None):
		super().__init__(name, 'text', False, default)

#编写Model的元类 ModelMetaclass
class ModelMetaclass(type):
	def __new__(cls, name, bases, attrs):
		if name=='Model':
			return type.__new__(cls, name, bases, attrs)
		tableName = attrs.get('__table__', None) or name
		logging.info('found model: %s (table: %s)' % (name, tableName))
		mappings = dict()
		fields = []
		primary_key = None
		for k, v in attrs.items():
			if isinstance(v, Field):
				logging.info('found mapping:%s ==>%s' % (k, v))
				mappings[k] = v
				if v.primary_key:
					if primary_key: #找到主键
						raise StandardError('Duplicate primary key for field:%s' % k)
					primaryKey = k
				else:
					fields.append(k)
		if not primaryKey:
			raise StandardError('primary key not found.')
		for k in mappings.keys():
			attrs.pop(k) #删掉类上的这些属性
		escaped_fields = list(map(lambda f: '%s' % f, fields)) #把fields 里的值都变成字符串
		attrs['__mappings__'] = mappings # 保存属性和列的映射关系
		attrs['__table__'] = tableName
		attrs['__primary_key__'] = primaryKey 
		attrs['__fields__'] = fields
		attrs['__select__'] = 'select %s, %s from %s' % (primaryKey, ','.join(escaped_fields), tableName)
		attrs['__insert__'] = 'insert into %s (%s, %s) values (%s)' % (tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
		attrs['__update__'] = 'update %s set %s where %s =?' % (tableName, ', '.join(map(lambda f: '%s =?' % (mappings.get(f).name or f), fields)), primaryKey)
		attrs['__delete__'] = 'delete from %s where %s =?' % (tableName, primaryKey)
		return type.__new__(cls, name, bases, attrs)

#编写基类Model
class Model(dict, metaclass=ModelMetaclass):
	def __init__(self, **kw):
		super(Model, self).__init__(**kw)

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r"'Model' object has no attribute '%s'" % key)

	def __setattr__(self, key, value):
		self[key] = value

	def getValue(self, key):
		return getattr(self, key, None)
	
	def getValueOrDefault(self, key):
		value = getattr(self, key, None)
		if value is None:
			field = self.__mappings__[key]
			if field.default is not None:
				value = field.default() if callable(field.default) else field.default
				logging.debug('using default value for %s:%s' % (key, str(value)))
				setattr(self, key, value)
		return value

	@classmethod
	async def findAll(cls, where=None, args=None, **kw):
		#通过where来寻找对象
		sql = [cls.__select__] #sql语句
		if where:
			sql.append('where')
			sql.append(where)
		if args is None:
			args = []
		orderBy = kw.get('orderBy', None)
		if orderBy:
			sql.append('order By')
			sql.append(orderBy)
		limit = kw.get('limit', None)
		if limit is not None:
			sql.append('limit')
			if isinstance(limit, int):
				sql.append('?')
				args.append(limit)
			elif isinstance(limit, tuple) and len(limit) == 2:
				sql.append('?, ?')
				args.extend(limit)
			else:
				raise ValueError('Invalid limit value: %s' % str(limit))

		rs = await select(' '.join(sql), args)
		return [cls(**r) for r in rs]

	@classmethod
	async def findNumber(cls, selectField, where=None, args=None):
		sql = ['select %s _num_ from %s' % (selectField, cls.__table__)]
		if where:
			sql.append('where')
			sql.append(where)
		rs = await select(' '.join(sql), args, 1)
		if len(rs) == 0:
			return None
		return rs[0][_num_]

	@classmethod
	async def find(cls, pk):
		rs = await select('%s where %s=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
		if len(rs) == 0:
			return None
		return cls(**rs[0])

	async def save(self):
		args = list(map(self.getValueOrDefault, self.__fields__))
		args.append(self.getValueOrDefault(self.__primary_key__))
		rows = await execute(self.__insert__, args)
		if rows != 1:
			logging.warn('failed to insert record: affected rows:%s' % rows)

	async def update(self):
		args = list(map(self.getValue, self.__fields__))
		args.append(self.getValue(self.__primary_key__))
		rows = await execute(self.__update__, args)
		if rows != 1:
			logging.warn('failed to update by primary key: affected rows:%s' % rows)

	async def remove(self):
		args = [self.getValue(self.__primary_key__)]
		rows = await execute(self.__delete__, args)
		if rows != 1:
			logging.warn('failed to remove by primary key: affected rows: %s' % rows)









