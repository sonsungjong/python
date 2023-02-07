import pymysql

connection = pymysql.connect(
        user="root",
        password="root",
        host="127.0.0.1",
        port=3307,
        database="newdb"
)

cursor = connection.cursor()

delete_query = "DELETE FROM emptable WHERE _id=2"

try:
    cursor.execute(delete_query)
    connection.commit()
    print("Record has been deleted")

except Exception as e:
    connection.rollback()
    print("Exception Occured : ", e)

connection.close()