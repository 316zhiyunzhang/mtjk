#!/usr/python3.5/bin/python3.5
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pymysql, datetime, traceback


# 发送邮件
def send_mail(sendstr):
    # 设置发件邮箱属性
    sender = 'mtjk_dailyreport@sina.com'
    subject = '微信公众号统计'
    smtpserver = 'smtp.sina.com'
    username = 'mtjk_dailyreport'
    password = '123@abc'

    # 设置收件人
    # receiver = ['harryyang@mytijian.com', 'xz@mytijian.com', 'hb@mytijian.com', 'qianjun@mytijian.com',
    #             'wangjian@mytijian.com', 'zf@mytijian.com', 'yaoyong@mytijian.com', 'jhlv@mytijian.com',
    #             'xiaochang@mytijian.com', 'zhangzhiyun@mytijian.com','lulihong@mytijian.com']

    receiver = ['zhangzhiyun@mytijian.com']
    try:
        msg = MIMEText(sendstr, 'html', 'utf-8')
        msg['From'] = "{}".format(sender)
        msg['To'] = ','.join(receiver)
        msg['Subject'] = Header(subject, 'utf-8')

        smtp = smtplib.SMTP()
        smtp.connect(smtpserver)
        smtp.login(username, password)
        smtp.sendmail(msg['From'], receiver, msg.as_string())
        smtp.quit()
        print('success!')
    except:
        f = open("wxmail.txt", 'a')
        traceback.print_exc(file=f)
        f.flush()
        f.close()


def getwxdata(conn):
    try:
        cur = conn.cursor()
        sql = '''SELECT
        t1.ref_date,
        t2. NAME,
        t1.new_user,
        t1.cancel_user,
        t1.cumulate_user,
        t1.new_bind_user,
        t1.count_bind_user,
        t1.from_other,
        t1.from_search,
        t1.from_card_share,
        t1.from_scan,
        t1.from_pay
    FROM
        lzh_wx_daily_count t1
    LEFT JOIN tb_hospital t2 ON t1.hospital_id = t2.id
    WHERE
        t1.ref_date = '{}'
    and t1.hospital_id != 0
    # AND t1.cumulate_user >= 500
    order by t1.cumulate_user desc,t1.count_bind_user DESC ;
    '''.format(datetime.date.today() - datetime.timedelta(days=1))
        cur.execute(sql)
        rst = cur.fetchall()
        if rst:
            return list(rst)
        else:
            return
    except:
        f = open("wxmail.txt", 'a')
        traceback.print_exc(file=f)
        f.flush()
        f.close()
    finally:
        cur.close()


def getSum(conn):
    try:
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = '''SELECT
	count(t2. NAME) as 'n_hospital',
	sum(t1.new_user) as 'n_new_user',
	sum(t1.cancel_user) as 'n_cancel_user',
	sum(t1.cumulate_user) as 'n_cumulate_user',
	sum(t1.new_bind_user) as 'n_new_bind_user',
	sum(t1.count_bind_user) as 'n_count_bind_user',
	sum(t1.from_other) as 'n_from_other',
	sum(t1.from_search) as 'n_from_search',
	sum(t1.from_card_share) as 'n_from_card_share',
	sum(t1.from_scan) as 'n_from_scan',
	sum(t1.from_pay) as 'n_from_pay'
FROM
	lzh_wx_daily_count t1
LEFT JOIN tb_hospital t2 ON t1.hospital_id = t2.id
WHERE
	t1.ref_date = '{}'
AND t1.hospital_id != 0
ORDER BY
	t1.cumulate_user DESC,
	t1.count_bind_user DESC;'''.format(datetime.date.today() - datetime.timedelta(days=1))
        cur.execute(sql)
        rst = cur.fetchone()
        if rst:
            return rst
        else:
            print('1')
            return
    except:
        f = open("wxmail.txt", 'a')
        traceback.print_exc(file=f)
        f.flush()
        f.close()
    finally:
        cur.close()


if __name__ == '__main__':
    conn = pymysql.Connect(host='rm-bp1nxe7521rz0v77go.mysql.rds.aliyuncs.com', user='mytijian',
                           passwd='mytijian', db='mytijian_dw', port=3306, charset='utf8')
    dt = getwxdata(conn)
    plus = getSum(conn)
    conn.close()
    tb_head = '<tr align="left" style="color:red"><td></td><td>体检中心</td><td>新关注</td><td>取消关注</td><td>总关注</td><td>新绑定</td><td>总绑定</td>' \
              '<td>其他</td><td>搜索</td><td>分享</td><td>扫码</td><td>支付</td></tr>'
    total_str = '<tr align="left" style="color:red"><td></td><td>合计：{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>' \
                '<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'
    tb_body = ''
    for i in dt:
        # 只展示总关注数>=500的数据
        if i[4] < 500:
            break
        par = ''
        tmp = '<td>{}</td>'.format(str(dt.index(i) + 1))
        for j in range(1, len(i)):
            sub = '<td>' + str(i[j]) + '</td>'
            tmp += sub
        par = '<tr>' + tmp + '</tr>'
        tb_body += par

    total = total_str.format(len(dt), plus.get('n_new_user'), plus.get('n_cancel_user'), plus.get('n_cumulate_user'),
                             plus.get('n_new_bind_user'), plus.get('n_count_bind_user'), plus.get('n_from_other'),
                             plus.get('n_from_search'), plus.get('n_from_card_share'), plus.get('n_from_scan'),
                             plus.get('n_from_pay'))
    str1 = '<!DOCTYPE html><html><head><title></title><meta charset="utf-8" /></head><body><h4>微信统计数据</h4><h5>数据日期：{}</h5>' \
           '报表仅展示总关注数>500的体检中心数据<br>其他：其他的关注来源<br>搜索：来自微信搜索<br>' \
           '分享：来自微信名片分享<br>扫码：来自扫描二维码<br>支付：其他三方公众号支付后关注<br>&nbsp<br>'.format(
        datetime.date.today() - datetime.timedelta(days=1))
    str2 = '<table style = "border-collapse: collapse; border-spacing: 0;" border = "1" cellspacing = "0" cellpadding = "0" >' \
           '{}{}{}</table >'.format(tb_head, total, tb_body)
    str3 = '</body></html>'
    mail_content = str1 + str2 + str3
    print(mail_content)
    # send_mail(mail_content)
