## My first webapp 加油！
##### 注明：这个小项目是我独自学习廖雪峰老师免费的python课程时完成的，期间经历了无数次挫败，但最终都坚持了下来，并完成了这个项目。在此给自己点个赞，同时感谢廖雪峰老师编写了如此棒的python课程。
#### 一、我们先来看看项目上线的整体效果
![](https://raw.githubusercontent.com/xpony/Graph-bed/master/img/20190919web1.png)
##### 首页长上边这样
![](https://raw.githubusercontent.com/xpony/Graph-bed/master/img/20190919web2.png)
##### 摄影页长这样
![](https://raw.githubusercontent.com/xpony/Graph-bed/master/img/20190919web3.png)
##### 文章内容页长这样
![](https://raw.githubusercontent.com/xpony/Graph-bed/master/img/20190919web5.png)
##### 注册页长这样
![](https://raw.githubusercontent.com/xpony/Graph-bed/master/img/20190919web6.png)
##### 管理页面长这样
##### 还有其它的一些细节就不逐一截图啦，大家可以访问我已经上线的网站体验哈，当然，本人也是刚入门的小白，技术有限，做的并不好，还请大家多多包涵，不要见笑。
#### 二、关于项目的分享与一些问题的说明
##### 分享是为了逼自己去更好的记录和学习，也是希望能给后边的人一点指引和帮助。在代码编写过程中，写了很多注释，有时会把自己的一些理解和学习心得写在旁边。项目虽小，但用来入门学习，却是一个不错的选择。尤其，对于那些同样通过廖雪峰老师的python课程学习的盆友，完成这个项目时，用来参考学习，可以更加高效，也可以避免很多坑。
##### 项目内容的一些说明：
- ##### python版本：python3   
- ##### 前端：css框架uikit 和一点 vue.js
- ##### 后端：完全python实现，使用的几个第三方库：asyncio、aiohttp、aiomysql、jinja2、markdown    

##### 需要注意的一些问题：
- ##### www目录下的schema.sql是本项目数据库和表初始化脚本，运行前需要正确配置自己的数据库账户和密码
- ##### markdown解析使用了第三方库markdown，开始使用了markdown2，但解析代码块时有些问题
- ##### 管理页的分页还略有问题，后边解决了会及时更新。若有盆友解决了，还望指导一下，互相学习，万分感谢。

#### 三、一点恳请
##### 为了后边盆友学习以及能正常运行此项目，所有代码我并未做任何改动，跟我上线跑的代码完全一致，毫无保留。因为我刚从小白一步步的走过来，非常知道小白是何种体验，一步一步走来有多么的艰难。所以，在此恳请大家，如果你发现此项目中的代码有什么漏洞，请不要借此去攻击我的小站，如果你愿意告诉我或帮我改进问题，我将万分感激！

