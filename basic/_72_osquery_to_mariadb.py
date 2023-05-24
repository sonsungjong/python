import os
import json
import subprocess
import mariadb

# osquery 실행결과 가져오기
def GetOsqueryResult(query):
    osquery_path = "C:\\Program Files\\osquery\\osqueryi.exe"
    cmd = [osquery_path, '--json', query]
    result = subprocess.check_output(cmd)
    return json.loads(result)

# MariaDB 연결
def Connect2Mariadb():
    return mariadb.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="root",
        database="system_info"
    )

# 데이터 삽입
def InsertDataToMariadb(cursor, data):
    for process in data:
        pid = process.get("pid")
        name = process.get("name")
        path = process.get("path")
        cmdline = process.get("cmdline")
        query = f"REPLACE INTO processes (pid, name, path, cmdline) VALUES ({pid}, '{name}', '{path}', '{cmdline}');"
        cursor.execute(query)

def main():
    query = "SELECT * FROM processes;"
    data = GetOsqueryResult(query)

    connection = Connect2Mariadb()
    cursor = connection.cursor()

    InsertDataToMariadb(cursor, data)

    connection.commit()
    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()








