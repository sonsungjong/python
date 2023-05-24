import pymysql

# 기존에 동일한 이름이 있다면 삭제하고 테이블을 새로 만드는 예제

connection = pymysql.connect(
        user="root",
        password="root",
        host="127.0.0.1",
        port=3307,
        database="newdb"
)

cursor = connection.cursor()

delete_existing_table = "drop table if exists emptable"
create_table_query = """create table emptable(_id int auto_increment primary key,
name varchar(20) not null)
"""

try:
    cursor.execute(delete_existing_table)
    print('Existing table has been deleted')
    cursor.execute(create_table_query)
    print('emptable Table has been created!')
except Exception as e:
    print('Exeception Occured : ',e)

connection.close()