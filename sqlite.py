# -*- coding: utf-8 -*-
import sqlite3,json

import sys

result=json.load(file('/var/www/html/uims/result.json'))
con=sqlite3.connect("/var/www/html/uims/ranking.db")
cur=con.cursor()

def insertSQL(result):
    number=result[0].encode('utf-8')
    cur.execute("INSERT INTO score(number) VALUES (?);", (number,))
    con.commit()
    result.pop(0)
    for m in result:
        cur.execute("UPDATE score SET %s = ? WHERE number=?;"%m[0].encode('utf-8'),(m[1].encode('utf-8'),number))
    con.commit()

if len(result) != 53:
    print "数据导入失败，请检查密码或科目数目"
    sys.exit()
else:
    insertSQL(result)
    f = open('/var/www/html/uims/result.json', 'w')
    res = json.dumps(result)
    f.write(res)
    f.close()











