#初始化数据库表的SQL脚本  执行：用root用户登录mysql,然后执行 \. schema.sql 即可
drop database if exists webapp;

create database webapp;  ##创建的数据库名称

use webapp;

grant select, insert, update, delete on webapp.* to 'root'@'localhost' identified by 'root123';

create table users (
	id varchar(50) not null,
	email varchar(50) not null,
	passwd varchar(50) not null,
	admin bool not null,
	name varchar(500) not null,
	image varchar(500) not null,
	create_at real not null,
	unique key idx_email (email),
	key idx_create_at (create_at),
	primary key (id)
) engine=innodb default charset=utf8;

create table blogs(
	id varchar(50) not null,
	user_id varchar(50) not null,
	user_name varchar(50) not null,
	user_image varchar(500) not null,
	name varchar(50) not null,
	summary varchar(200) not null,
	content mediumtext not null,
	create_at real not null,
	key idx_create_at (create_at),
	primary key (id)
) engine=innodb default charset=utf8;

create table comments(
	id varchar(50) not null,
	blog_id varchar(50) not null,
	user_id varchar(50) not null,
	user_name varchar(50) not null,
	user_image varchar(500) not null,
	content mediumtext not null,
	create_at real not null,
	key idx_create_at (create_at),
	primary key (id)
) engine=innodb default charset=utf8;

create table photos(
	id varchar(50) not null,
	user_id varchar(50) not null,
	user_name varchar(50) not null,
	url varchar(500) not null,
	name varchar(50) not null,
	create_at real not null,
	key idx_create_at (create_at),
	primary key (id)
) engine=innodb default charset=utf8;




