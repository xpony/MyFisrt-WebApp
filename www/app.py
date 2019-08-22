#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

# 编写webapp基本骨架
import logging; logging.basicConfig(level=logging.INFO) #配置日志级别
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web

def index(request): #处理首页请求 /
	return web.Response(body=b'<h1>My-WebApp</h1>', content_type='text/html')

async def init(loop):
	app = web.Application(loop=loop) #生成app对象
	app.router.add_route('GET', '/', index) #设置路由
	srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000) #创建服务器
	logging.info('server started at http://127.0.0.1:9000……')
	# return srv  为什么要返回srv?

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()










