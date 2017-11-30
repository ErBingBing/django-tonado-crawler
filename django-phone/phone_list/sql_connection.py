import pymysql

def connection(sql):
    db = pymysql.connect("10.3.0.42", "root", "38,5BtC8.pkS2XX9", "phone_ali", charset='utf8')
   
    cursor = db.cursor()
    print '1111111111111111111111111111111111123'
    try:

        cursor.execute(sql)
        results = cursor.fetchall()
        print(results)

    except:
        db.rollback()
    finally:
        db.close()
