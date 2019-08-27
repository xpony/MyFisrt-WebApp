#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

#编写web框架，来处理http请求
import asyncio, os, inspect, logging, functools
from urllib import parse
from aiohttp import web
from apis import APIError # 这是个自己编写的模块

#两个装饰器，使用装饰器的函数会增加两个属性
def get(path): #一个函数通过get装饰会附带url信息，类型是GET
	def decorator(func):
		@functools.wraps(func) #把func函数的名字绑定到wrapper上
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = 'GET'  #给函数增加了两个属性
		wrapper.__route__ = path
		return wrapper
	return decorator

def post(path): #一个函数通过post装饰会附带url信息，类型是POST
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__method__ = 'POST'
		wrapper.__route__ = path
		return wrapper
	return decorator

#检查函数的参数类型,
def get_required_kw_args(fn): #返回fn所有有默认值的命名关键字参数
	args = []
	params = inspect.signature(fn).parameters #返回一个OrderedDict，包含了fn所有参数类型
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:#是关键字参数且有默认值(*，b=int)
			args.append(name)
	return tuple(args) #list变tuple

def get_named_kw_args(fn): #返回fn的所有命名关键字参数
	args = []
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			args.append(name)
	return tuple(args)

def has_named_kw_args(fn): #判断fn是否有命名关键字参数，有返回True
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.KEYWORD_ONLY:
			return True

def has_var_kw_arg(fn): #判断参数里是否有 **kw 既关键字参数(是个dict)
	params = inspect.signature(fn).parameters
	for name, param in params.items():
		if param.kind == inspect.Parameter.VAR_KEYWORD:
			return True

def has_request_arg(fn): #判断fn是否有request参数，且是最后一个参数
	params = inspect.signature(fn).parameters
	found = False
	for name, param in params.items():
		if name == 'request':  #参数是request
			found = True
			continue								#  *args 可变参数                               	命名关键字参数									**kw  关键字参数               
		if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
			raise ValueError('request parameter must be the last named parameter in function:%s' % fn.__name__)
	return found


class RequestHandler(object):
	def __init__(self, app, fn):
		self._app = app
		self._func = fn
		self._has_request_arg = has_request_arg(fn)
		self._has_var_kw_arg = has_var_kw_arg(fn)
		self._has_named_kw_args = has_named_kw_args(fn)
		self._named_kw_args = get_named_kw_args(fn)
		self._required_kw_args = get_required_kw_args(fn)

	async def __call__(self, request):
		kw = None
		if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
			if request.method == 'POST':
				if not request.content_type:
					return web.HTTPBadRequest('Missing content_type.')
				ct = request.content_type.lower()
				if ct.startswith('application/json'): #判断字符串是不是以它开始的
					params = await request.json() #获取json内容
					if not isinstance(params, dict):
						return web.HTTPBadRequest('JSON body must be object.')
					kw = params #json内容放到了kw

				elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
					params = await request.post()
					kw = dict(**params)
				else:
					return web.HTTPBadRequest('Unsupported content_type: %s' % request.content_type)
			if request.method == 'GET':
				qs = request.query_string #是一个字符串，url中？后的所有值
				if qs:
					kw = dict()
					for k, v in parse.parse_qs(qs, True).items(): #循环出url中的参数
						kw[k] = v[0]
					print(99999999999999999)
					print(kw)
		if kw is None:
			kw = dict(**request.match_info) #路径参数
		else:
			if not self._has_var_kw_arg and self._named_kw_args:#挑出所有命名关键参数
				copy = dict()
				for name in self._named_kw_args:
					if name in kw:
						copy[name] = kw[name]
				kw = copy
			for k, v in request.match_info.items():
				if k in kw:
					logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
				kw[k] = v
		if self._has_request_arg:
			kw['request'] = request
		if self._required_kw_args:#有默认值的关键字参数
			for name in self._required_kw_args:
				if not name in kw:
					return web.HTTPBadRequest('Missing argument: %s' % name)
		logging.info('call with args: %s' % str(kw))
		try:
			r = await self._func(**kw)
			return r
		except APIError as e:
			raise dict(error=e.error, data=e.data, message=e.message)


def add_static(app): #静态资源路径
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
	app.router.add_static('/static/', path)
	logging.info('add static: %s ==>%s' % ('/static/', path))

def add_route(app, fn):  #fn即url函数
	method = getattr(fn, '__method__', None)
	path = getattr(fn, '__route__', None)
	if path is None or method is None:
		raise ValueError('@get or @post not defined in %s.' % str(fn))
	if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
		fn = asyncio.coroutine(fn)
	logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
	app.router.add_route(method, path, RequestHandler(app, fn)) #添加路由时三个参数：1、请求类型 2、url路径 3、绑定响应函数

def add_routes(app, module_name):
	n = module_name.rfind('.') #返回.最后出现的位置
	if n == (-1): #没找到 . 即没有后缀名， 直接导入
		mod = __import__(module_name, globals(), locals())
	else:
		name = module_name[n+1:] #切片，拿到.后的内容
		mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
	for attr in dir(mod): #返回mod模块的所有属性方法列表
		if attr.startswith('_'):
			continue
		fn = getattr(mod, attr)
		if callable(fn):
			method = getattr(fn, '__method__', None)
			path = getattr(fn, '__route__', None)
			if method and path:
				add_route(app, fn)


