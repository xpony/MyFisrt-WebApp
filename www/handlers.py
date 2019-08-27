#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'xpony'

'url handlers'

import re, time, json, logging, hashlib, base64, asyncio
from coroweb import get, post
from models import User, Comment, Blog, next_id
from aiohttp import web
from apis import APIValueError, APIResourceNotFoundError, APIError, APIPermissionError
from config import configs
import markdown2
from apis import Page

#设置cookie
COOKIE_NAME = 'xponysession'
_COOKIE_KEY = configs.session.secret

#检查reques对象是否有user属性 创建日志的api使用
def check_admin(request):
	if request.__user__ is None or not request.__user__.admin:
		return APIPermissionError()

#确认页数信息 日志分页api使用
def get_page_index(page_str):
	p = 1
	try:
		p = int(page_str)
	except Exception as e:
		pass
	if p < 1:
		p = 1
	return p 

#将text文本转换成html  单篇访问日志的api使用
def text2html(text):
	lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
	return ''.join(lines)

# 计算加密cookie:
def user2cookie(user, max_age): #把用户信息变成cookie用的字符串
	expires = str(int(time.time() + max_age))
	s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
	L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
	return '-'.join(L)

#解析用户cookie
async def cookie2user(cookie_str):
	if not cookie_str:
		return None
	try:
		L = cookie_str.split('-')
		if len(L) != 3:
			return None
		uid, expires, sha1 = L
		if int(expires) < time.time():
			return None
		user = await User.find(uid)
		if user is None:
			return None
		s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
		if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
			return None
		user.passwd = '******'
		return user
	except Exception as e:
		logging.exception(e)
		return None



# @get('/')
# async def index(request):
# 	users = await User.findAll()
# 	return {
# 		'__template__': 'test.html', # MVC中的V 即 View 视图
#         'users': users  # MVC中的M Model 即传给View的数据
# 	}

@get('/') #首页
async def index(*, page='1'): #路径上的参数是通过coroweb.py里的RequestHandler(）捕获之后传到url函数里的
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	page = Page(num, page_index=page_index) ##这里必须把新的page_index传进去！否则翻页功能有问题。
	if num == 0:
		blogs = []
	else:
		blogs = await Blog.findAll(orderBy='create_at desc', limit=(page.offset, page.limit))
	return {
		'__template__': 'blogs.html',
		'page': page,
		'blogs': blogs
	}

#用户注册页
@get('/register')  
async def register():
	return {
		'__template__': 'register.html'
	}

# @get('/api/users') #测试
# async def api_get_users():
# 	users = await User.findAll(orderBy='create_at desc') #按创建时间且按降序对记录进行排序
# 	for u in users:
# 		u.passwd = '*********'
# 	return dict(users=users)

#用户注册API
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}')
@post('/api/users')
async def api_register_user(*, email, name, passwd):
	if not name or not name.strip():
		raise APIValueError('name')
	if not email or not _RE_EMAIL.match(email):
		raise APIValueError('email')
	if not passwd or not _RE_SHA1.match(passwd):
		raise APIValueError('passwd')
	user_e = await User.findAll('email=?', [email])
	if len(user_e) > 0:
		raise APIError('register:failed', 'email', 'Email is already in use.')
	uid = next_id()
	sha1_passwd = '%s:%s' % (uid, passwd)
	user = User(id=uid, name=name.strip(),email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
	await user.save() #保存到数据库
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '*****'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')#json中有中文时，要把ensure_ascii改成False才能显示
	return r

#用户登录页
@get('/signin')
async def signin():
	return {
		'__template__':'signin.html'
	}

#用户登录API
@post('/api/authenticate')
async def authenticate(*, email, passwd):
	if not email:
		raise APIValueError('email', 'Invalid email')
	if not passwd:
		raise APIValueError('passwd', 'Invalid passwd')
	users = await User.findAll('email=?', [email])
	if len(users) == 0:
		raise APIValueError('email', 'Email not exist')
	user = users[0]
	#计算哈希，检查密码
	sha1 = hashlib.sha1()
	sha1.update(user.id.encode('utf-8'))
	sha1.update(b':')
	sha1.update(passwd.encode('utf-8'))	
	if user.passwd != sha1.hexdigest():
		raise APIValueError('passwd', 'Invalid passwd')
	r = web.Response()
	r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
	user.passwd = '******'
	r.content_type = 'application/json'
	r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
	return r

#用户退出登录
@get('/signout')
async def signout(request):
	referer = request.headers.get('Referer')
	r = web.HTTPFound(referer or '/')
	r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
	logging.info('user signed out.')
	return r

#日志创建页
@get('/manage/blogs/create')
async def manage_create_blog():
	return {
		'__template__': 'manage_blog_edit.html',
		'id': '',
		'action': '/api/blogs',
	}

#创建日志的api 日志信息提到到这里，通过这里来提交到数据库
@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
	check_admin(request) #检查request对象身上是否绑定了user
	if not name or not name.strip():
		raise APIValueError('name', 'name cannot be empty.')
	if not summary or not summary.strip():
		raise APIValueError('summary', 'summary cannot be empty')
	if not content or not content.strip():
		raise APIValueError('content', 'content cannot be empty')
	blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
	await blog.save()
	return blog

#日志分页显示的api
@get('/api/blogs')
async def api_blogs(*, page='1'):
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	p = Page(num, page_index)
	if num == 0:
		return dict(page=p, blogs=())
	blogs = await Blog.findAll(orderBy='create_at desc', limit=(p.offset, p.limit))
	return dict(page=p, blogs=blogs)

#日志管理页
@get('/manage/blogs')
async def manage_blogs(*, page='1'):
	page_index = get_page_index(page)
	num = await Blog.findNumber('count(id)')
	page = Page(num, page_index=page_index) ##这里必须把新的page_index传进去！否则翻页功能有问题。
	if num == 0:
		blogs = []
	else:
		blogs = await Blog.findAll(orderBy='create_at desc', limit=(page.offset, page.limit))
	return {
		'__template__': 'manage_blogs.html',
		'page_index': get_page_index(page),
		# 'page': page,
		# 'blogs': blogs
	}	

#谋篇日志访问页  返回日志和其评论
@get('/blog/{id}')
async def get_blog(id):
	blog = await Blog.find(id)
	comments = await Comment.findAll('blog_id=?', [id], orderBy='create_at desc')
	for c in comments:
		c.html_content = text2html(c.content)
	blog.html_content = markdown2.markdown(blog.content)
	return {
		'__template__': 'blog.html',
		'blog': blog,
		'comments': comments
	}

#获取谋篇日志的api
@get('/api/blogs/{id}')
async def api_get_blog(*, id):
	blog = await Blog.find(id)
	return blog

#删除谋篇日志
@post('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
	check_admin(request)
	blog = await Blog.find(id)
	await blog.remove()
	return dict(id=id)

#修改谋篇日志
@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }

#添加评论的api
@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    await comment.save()
    return comment