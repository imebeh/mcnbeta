mcnbeta
=======

cnBeta.com的全文RSS


简单的cnBeta抓取工具，方便生成全文的RSS
新闻及热评来源是移动版的cnBeta
关于cnBeta，移步 `http://zh.wikipedia.org/zh/CnBeta.com`

对python的很多框架不熟悉，随便做的一个能运行的脚本

运行

 	`python mcnbetaui.py 80`

在浏览器访问 http://localhost:80 即可。

-	`http://localhost/feed`			RSS订阅源
-	`http://localhost`				显示最新30条新闻
-	`http://localhost/10`       或
-	`http://localhost/count/10`		显示最新10条新闻，“count/”省略也可以
-	`http://localhost/131191`			显示cb编号为131191的新闻
-	`http://localhost/131191/next`	显示cb编号为131191的新闻的下一条新闻
-	`http://localhost/131191/previous`显示cb编号为131191的新闻的上一条新闻
-	`http://localhost/s2c3`     或
-	`http://localhost/start2count3`	从最新的第二条开始显示3个新闻
-	`http://localhost/update`   或
-	`http://localhost/update/3`		更新第3页的所有新闻，默认是第一页
下次更新会统一一下地址

已知问题：

	1、使用/s1c10方式访问时，数量大于缓冲的新闻数量会报错
	2、Chrome/Firefox/Safari PC版图片高度不能自适应，Opera（可设置是否发送Referrer，不用iframe处理也可以正常显示图片）/Opera Mobile/Safari 移动版正常，IE9不能正常使用不能解码base64后的img标签，veer的浏览器不能显示图片