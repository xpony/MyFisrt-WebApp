#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

# 编写webapp基本骨架
import logging; logging.basicConfig(level=logging.INFO) #配置日志级别
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
import orm
from coroweb import add_routes, add_static

def init_jinja2(app, **kw): #加入jinja2的自主注册
	logging.info('init jinja2……')
	options = dict(
		autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
	)
	path = kw.get('path', None)
	if path is None:
		path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
	logging.info('set jinja2 template path: %s' % path)
	env = Environment(loader=FileSystemLoader(path), **options)
	filters = kw.get('filters', None)
	if filters is not None:
		for name, f in filters.items():
			env.filters[name] = f
	app['__templating__'] = env


#记录url的日志函数
async def logger_factory(app, handler):
	async def logger(request):
		logging.info('Request:%s %s' % (request.method, request.path))
		return (await handler(request))
	return logger

async def data_factory(app, handler):
	async def parse_data(request):
		if request.method == 'POST':
			if request.content_type.startswith('application/json'):
				request.__data__ = await request.json()
				logging.info('request json:%s' % str(request.__data__))
			elif request.content_type.startswith('application/x-www-form-urlencoded'):
				request.__data__ = await request.post()
				logging.info('request form:%s' % str(request.__data__))
		return (await handler(request))
	return parse_data

#把返回值转换成web.Response对象
async def response_factory(app, handler):
	async def response(request):
		logging.info('Response handler……')
		r = await handler(request)     #响应的内容形式  handle就是url函数
		if isinstance(r, web.StreamResponse):
			return r
		if isinstance(r, bytes):
			resp = web.Response(body=r)
			resp.content_type = 'application/octet-stream'
			return resp
		if isinstance(r, str):
			if r.startswith('redirect:'):
				return web.HTTPFound(r[9:])
			resp = web.Response(body=r.encode('utf-8'))
			resp.content_type = 'text/html; charset=utf-8'
			return resp
		if isinstance(r, dict):
			template = r.get('__template__')
			if template is None:
				resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
				resp.content_type = 'application/json; charset=utf-8'
				return resp
			else:
				resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
				resp.content_type = 'text/html;charset=utf-8'
				return resp
		if isinstance(r, int) and r >= 100 and r < 600:
			return web.Response(r)
		if isinstance(r, tuple) and len(r) ==2:
			t, m = r 
			if isinstance(t, int) and t >= 100 and t < 600:
				return web.Response(r, str(m))
		resp = web.Response(body=str(r).encode('utf-8'))
		resp.content_type = 'text/plain; charset=utf-8'
		return resp
	return response

#计算发表时间
def datetime_filter(t): 
	delta = int(time.time() -t)
	if delta < 60:
		return u'1分钟前'
	if delta < 3600:
		return u'%s分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s小时前' % (delta // 3600)
	if delta < 604800:
		return u'%s天前' % (delta // 86400)
	dt = datetime.fromtimestamp(t)
	return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


# def index(request): #处理首页请求 /
# 	return web.Response(body=b'<h1>My-WebApp</h1>', content_type='text/html')

async def init(loop):
	await orm.create_pool(loop, user='root', password='root123', db='webapp')
	#生成app对象   并且添加了个中间件 middleware是一种拦截器
	app = web.Application(loop=loop, middlewares=[
		logger_factory, response_factory
	]) 
	init_jinja2(app, filters=dict(datetime=datetime_filter)) #加入jinja2的自主注册 过滤器添加进去
	add_routes(app, 'handlers') #在coroweb.py  自动扫描handles模块，把符合的url添加进路由
	add_static(app)
	# app.router.add_route('GET', '/', index) #设置路由
	srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000) #创建服务器
	logging.info('server started at http://127.0.0.1:9000……')
	return srv  #为什么要返回srv?

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()










