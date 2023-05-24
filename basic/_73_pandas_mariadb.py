# pip install pymysql [또는 pip install mariadb]
# pip install numpy scipy matplotlib ipython scikit-learn pandas pillow imageio

import pandas as pd
import pymysql
import mariadb

# pymysql.connect() 또는 mariadb.connect() 사용해서 연결
def select_mariadb(query):
    dbconn = pymysql.connect(
        user='root',
        password='root',
        host='127.0.0.1',
        port=3307,
        database='newdb'
    )

    # 마리아DB to pandas DataFrame
    query_result = pd.read_sql(query, dbconn)
    dbconn.close()

    return query_result

def insert_mariadb(query):
    try:
        mydb = pymysql.connect(
            user='root',
            password='root',
            host='127.0.0.1',
            port=3307,
            database='newdb',
            autocommit=True
        )
        dbconn = mydb.cursor()
        # list to mariaDB INSERT
        dbconn.execute(query)
        dbconn.close()
        return 1
    except pymysql.Error as e:
        print(f'Error connecting to MariaDB: {e}')
        dbconn.close()
        return -1

if __name__ == '__main__':
    # INSERT
    # lst = [['사람1','남자'], ['사람2','woman']]
    # list -> DataFrame
    # df = pd.DataFrame(lst)
    # DataFrame -> list
    # lst2 = df.values.tolist()
    sql = "INSERT INTO employee (emp_name, emp_gender) VALUES ('지우','남성')"
    insert_result = insert_mariadb(sql)

    # SELECT
    sql = "SELECT * FROM employee"
    df = select_mariadb(sql)
    print(df)