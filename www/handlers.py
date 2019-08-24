#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

'url handlers'

import re, time, json, logging, hashlib, base64, asyncio
from coroweb import get, post
from models import User, Comment, Blog, next_id

# @get('/')
# async def index(request):
# 	users = await User.findAll()
# 	return {
# 		'__template__': 'test.html', # MVC中的V 即 View 视图
#         'users': users  # MVC中的M Model 即传给View的数据
# 	}

@get('/')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=1566616682.698303),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }