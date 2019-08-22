#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

import time, uuid
from orm import Model, StringField, BooleanField, TextField, FloatField
#编写 user, blog, comment三个model

def next_id():
	return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex) #用时间戳和UUID4(基于随机数)生成唯一ID

class User(Model):
	__table__ = 'users'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	email = StringField(ddl='varchar(50')
	passwd = StringField(ddl='varchar(50)')
	admin = BooleanField()
	name = StringField(ddl='varchar(50)')
	image = StringField(ddl='varchar(500)')
	create_at = FloatField(default=time.time)

class Blog(Model):
	__table__ = 'blogs'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50')
	user_image = StringField(ddl='varchar(50)')
	name = StringField(ddl='varchar(50)')
	summary = StringField(ddl='varchar(200)')
	content = TextField()
	create_at = FloatField(default=time.time)

class Comment(Model):
	__table__ = 'contents'

	id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
	blog_id = StringField(ddl='varchar(50)')
	user_id = StringField(ddl='varchar(50)')
	user_name = StringField(ddl='varchar(50)')
	user_image = StringField(ddl='varchar(50)')
	content = TextField()
	create_at = FloatField(default=time.time)



#####测试User信息插入数据库 ==> 成功插入！
# import orm
# import asyncio

# async def test(loop):
#     await orm.create_pool(loop, user='root', password='root123', db='webapp')
#     u = User(name='xpony', email='xpony.red@gmail', passwd='mayizhao1997', image='about:blank')
#     await u.save()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(test(loop))
# loop.run_forever()













