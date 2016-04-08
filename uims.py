#-*-coding:utf8;-*-
#qpy:2
#qpy:console
import re
import urllib2, urllib, cookielib, json
from hashlib import md5
import sqlite3
import sys

import time

number = sys.argv[1]
passwd = sys.argv[2]
if len(passwd)==0:
    print "密码为空"
inp = md5('UIMS' + number + passwd).hexdigest()

def ranking(username,number,averScore):
    '''插入姓名和平均分'''
    con = sqlite3.connect("/var/www/html/uims/ranking.db")
    cur = con.cursor()
    cur.execute('INSERT INTO ranking(username,number,averScore) VALUES (?,?,?);',(username.decode('utf-8'),number,averScore))
    con.commit()

def insertSQL(number, passwd):
    '''插入账号密码'''
    con = sqlite3.connect("/var/www/html/uims/ranking.db")
    cur = con.cursor()
    cur.execute('INSERT INTO account(number,passwd) VALUES (?,?)', (number, passwd))
    con.commit()



def checkAccount(number):
    '''检查账号是否存在'''
    con = sqlite3.connect("/var/www/html/uims/ranking.db")
    cur = con.cursor()
    cur.execute('SELECT number FROM account WHERE number=?;', (number,))
    con.commit()
    if cur.fetchall():
        print "该同学成绩已存在"
        sys.exit()


checkAccount(number)


url = 'http://uims.jlu.edu.cn/ntms/userLogin.jsp?reason=login'
url_login = ' http://uims.jlu.edu.cn/ntms/j_spring_security_check'
header = {
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
}

cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)
request_pre = urllib2.Request(url, headers=header)
response_pre = opener.open(request_pre).read()
data = urllib.urlencode({
    'j_username': number,
    'j_password': inp

})
request_login = urllib2.Request(url_login, data)
response_login = opener.open(request_login).read()
data_query = json.dumps({"tag": "archiveScore@queryCourseScore", "branch": "latest", "params": {}, "rowlimit": 15,})
request_info=urllib2.Request('http://uims.jlu.edu.cn/ntms/action/getCurrentUserInfo.do')
response_info=opener.open(request_info).read()
username=re.findall('"nickName":"(.*?)"',response_info)[0]
print username
request_last_score = urllib2.Request('http://uims.jlu.edu.cn/ntms/service/res.do', data_query, header)
response_last_score = opener.open(request_last_score).read()
courName = re.findall('"courName":"(.*?)"', response_last_score)
scoreNum = re.findall('"scoreNum":"(.*?)"', response_last_score)
adviceCredit = re.findall('"adviceCredit":"(.*?)"', response_last_score)
type5 = re.findall('"type5":"(.{4})".{24,50}"courName"',response_last_score)
sum_score = 0
result = [number]
result_score = {}
result_tmp = []
result_adviceCredit = {}

jujie = 0
jishengchong = 0
courName_list = ["临床肿瘤学", "神经病学A", "儿科学A", "妇产科学A", "外科学A", "内科学A", "人体寄生虫学", "局部解剖学", "基础综合考试", "中医学", "影像诊断学", "外科总论",
                 "检体诊断学", "临床基础课综合实习", "实验诊断学", "核医学B", "心电诊断学", "超声诊断学", "基础医学专业英语", "医学文献检索", "分子生物学", "预防医学", "药理学",
                 "医学遗传学", "形势与政策Ⅰ", "医学微生物学", "病理解剖学", "大学英语BⅣ", "医学免疫学", "病理生理学", "数据库及程序设计基础", "细胞生物学",
                 "毛泽东思想和中国特色社会主义理论体系概论", "大学英语BⅢ", "生理学", "生物化学", "大学计算机基础", "普通心理学", "卫生法学", "有机化学E", "组织学与胚胎学",
                 "人体解剖学", "有机化学实验D", "大学物理及实验A", "中国近现代史纲要", "马克思主义基本原理概论", "大学英语BⅡ", "思想道德修养与法律基础", "大学英语BⅠ",
                 "无机化学实验D", "无机化学D", "医用数学C"]
for i in range(len(courName)):
    if courName[i] not in courName_list:
        continue
    elif courName[i] == "局部解剖学":
        if jujie == 1:
            continue
        else:
            jujie = 1
    elif courName[i] == "人体寄生虫学":
        if jishengchong == 1:
            continue
        else:
            jishengchong = 1
    result_tmp = [courName[i], scoreNum[i], adviceCredit[i]]
    result.append(result_tmp)
    # result_score[courName[i]] = scoreNum[i]
    # result_adviceCredit[courName[i]] = adviceCredit[i]
    if float(scoreNum[i])<60:
        continue
    sum_score = sum_score + float(scoreNum[i]) * float(adviceCredit[i])
average = sum_score / 205.5
print "你的平均分为："+ str(average)

if len(result) == 53:
    insertSQL(number, passwd)
    ranking(username,number,average)

    f = open('/var/www/html/uims/result.json', 'w')
    res = json.dumps(result)
    f.write(res)
    f.close()

else:
    print "导入成绩失败"
    print len(result)
    print "失败原因：科目不为52门 或 密码错误"


#print result_adviceCredit
#print result_score
