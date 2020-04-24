#!/usr/bin/env python
# coding=utf-8
'''
@Author: 以谁为师
@Website: attacker.club
@Date: 2020-04-20 22:16:53
@LastEditTime: 2020-04-24 08:25:50
@Description:
'''
import jinja2
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr


RENDER_HTML_TEMPLATE = """<html>
<head>
  <style type="text/css">
        body {
            font: 18px/1.5 Helvetica Neue, Helvetica, Arial, Microsoft Yahei, Hiragino Sans GB, Heiti SC, WenQuanYi Micro Hei, sans-serif;
        }
    
        div>div {
            color: blue;
        }
        .code{
            font-size: 12px;
            color: red;
        }

         ul {
            background-color: black;
        }

        ul>li {
            list-style: none;
            font-size: 20px;
            color: white;
        }
    </style>

</head>
<body>

    <h2>接收到[{{results.task}}]任务</h2>
    <p> 执行详细命令: </P>
    <hr>
    <span class="code">{{results.code}} </span> 
    <hr>


    <div>
        <p>输出:</P>
        <hr>
        
        <ul>
      
         {% for line in  results.output  %}
             <li>{{line}} </li>
         {% endfor %}
       
        </ul>
        
     
        <strong>Total </strong>: {{results.time}}
    </div>


   {% for line in results.data  %}
   <p> {{line.alert}} </p>
    {% endfor %}

</body>
</html>

"""


def template(data):
    res = jinja2.Template(source=RENDER_HTML_TEMPLATE).render(results=data)
    return res


def send(From, email, password, smtp, results):
    html = template(results)
    mail_sender = email    # 发件人邮箱账号
    mail_pass = password              # 发件人邮箱密码
    mail_user = From      # 收件人邮箱账号，我这边发送给自己
    ret = True
    try:
        msg = MIMEText(html, 'html', 'utf-8')
        # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        msg['From'] = formataddr(["管理员", mail_sender])
        # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        msg['To'] = formataddr(["robot", mail_user])
        msg['Subject'] = "来着robot的回复"                # 邮件的主题，也可以说是标题

        server = smtplib.SMTP_SSL(smtp, 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(mail_sender, mail_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.sendmail(mail_sender, [mail_user, ], msg.as_string())
        server.quit()  # 关闭连接
    except Exception:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        ret = False
    return ret


if __name__ == '__main__':
    template('dict')
