import pymysql

# insert

connection = pymysql.connect(
        user="root",
        password="root",
        host="127.0.0.1",
        port=3307,
        database="newdb"
)

cursor = connection.cursor()

name = input('Enter your name : ')

insert_query = """insert into emptable(name) values('%s')"""%(name)

try:
    cursor.execute(insert_query)
    connection.commit()
    print("Name is successfully inserted!")
except Exception as e:
    connection.rollback()
    print("Exception Occured : ",e)

connection.close()