import pymysql
# import mariadb

connection = pymysql.connect(
        user="root",
        password="root",
        host="127.0.0.1",
        port=3307,
        database="newdb"
)

cursor = connection.cursor()
sql_query = "SELECT VERSION()"

try:
    cursor.execute(sql_query)
    data = cursor.fetchone()
    print("Database Version : %s" %data)
except Exception as e:
    print("Exception : ", e)

connection.close()