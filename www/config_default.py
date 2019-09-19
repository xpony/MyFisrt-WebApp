#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
默认配置  本地开发环境
'''

__author__ = 'xpony'

configs = {
	'debug': True,
	'db': {
		'host': '127.0.0.1',
		'port': 3306,
		'user': 'root',  # 数据库登录名
		'password': 'root123', # 数据库登录密码
		'db': 'webapp'
	},
	'session': {
		'secret': 'xxxx'
	}
}





