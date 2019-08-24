#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Configuration
'''

__author__ = 'xpony'

import config_default

class Dict(dict):

	def __init__(self, names=(), values=(), **kw):
		super().__init__(**kw)
		for k, v in zip(names, values):#返回对应元素组成tuple的List
			self.[k] = v

	def __getattr__(self, key):
		try:
			return self[key]
		except KeyError:
			raise AttributeError(r" 'Dict' object has no attribute '%s' " % key)
	
	def __setattr__(self, key, value):
		self[key] = value

def merge(defaults, override):
	r = {}
	for k, v in defaults.items():  #override里的相同值覆盖掉default里的
		if k in override:
			if isinstance(v, dict): #扫描到最后一层dict
				r[k] = merge(v, override[k])
			else:
				r[k] = override[k]
		else:
			r[k] = v
	return r

def toDict(d):
	D = Dict()
	for k, v in d.items():
		D[K] = toDict(V) if isinstance(v, dict) else v
	return D 

configs = config_default.configs

try:
	import config_override
	configs = merge(configs, config_override.configs)
except ImportError:
	pass

configs = toDict(configs)


