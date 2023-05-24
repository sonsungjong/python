import pymysql

connection = pymysql.connect(
        user="root",
        password="root",
        host="127.0.0.1",
        port=3307,
        database="newdb"
)

cursor = connection.cursor()

update_query = "UPDATE emptable SET name='John Park' WHERE _id=2"

try:
    cursor.execute(update_query)
    connection.commit()
    print("Record Updated!")

except Exception as e:
    print("Exception Occured : ", e)
    connection.rollback()

connection.close()