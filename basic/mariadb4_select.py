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

sql_query = "SELECT * FROM emptable"

try:
    cursor.execute(sql_query)
    results = cursor.fetchall()

    for record in results:
        _id = record[0]
        name = record[1]
        print("ID : %d and Name : %s" %(_id, name))

except Exception as e:
    print("Exception Occured : ", e)

connection.close()