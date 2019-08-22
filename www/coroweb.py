#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

#编写web框架，来处理http请求
import asyncio, os, inspect, logging, functools
from urllib import parse
from aiohttp import web
# from apis import APIError # 这是个自己编写的模块

#两个装饰器，使用装饰器的函数会增加两个属性
def get(path): #一个函数通过get装饰会附带url信息，类型是GET
	def decorator(func):
		@functools.wraps(func) #把func函数的名字绑定到wrapper上
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__methord__ = 'GET'  #给函数增加了两个属性
		wrapper.__route__ = path
		return wrapper
	return decorator

def post(path): #一个函数通过post装饰会附带url信息，类型是POST
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kw):
			return func(*args, **kw)
		wrapper.__methord__ = 'POST'
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


class RequestsHandler(object):
	def __init__(self, app, fn):
		self._app = app
		self._func = fn
		self.has





