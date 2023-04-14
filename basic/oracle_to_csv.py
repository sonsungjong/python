# oracle(KO16MSWIN949) 데이터베이스 테이블을 csv(utf-8)로 추출하기 위한 프로그램
import csv
import cx_Oracle
import os

def Oracle2Csv(a_host_ip, a_port, a_service_name, a_id, a_pw, a_table_name, a_src_charset, a_dst_charset="utf-8"):
    CHARSET = f'KOREAN_KOREA.{a_src_charset}'
    # 오라클 환경변수 설정
    os.environ["NLS_LANG"] = CHARSET

    # 오라클 DB연결
    dsn = cx_Oracle.makedsn(a_host_ip, a_port, a_service_name)
    connection = cx_Oracle.connect(a_id, a_pw, dsn)

    # 쿼리 실행
    cursor = connection.cursor()
    query = f'SELECT * FROM {a_table_name}'
    cursor.execute(query)           # 커서에 SELECT 결과를 저장

    file_name = f'{a_table_name}.csv'
    # SELECT 결과를 CSV 파일로 저장
    with open(file_name, "w", newline="", encoding=a_dst_charset) as csvfile:
        writer = csv.writer(csvfile)

        # 컬럼명 저장
        writer.writerow([col[0] for col in cursor.description])

        # 결과 저장
        for row in cursor:
            writer.writerow(row)

    # 리소스 정리
    cursor.close()
    connection.close()

TABLE_NAME = input('input your table name>>')
Oracle2Csv("localhost", 1521, "XE", "lignex1", "lignex1", TABLE_NAME, "KO16MSWIN949")
print(f'{TABLE_NAME} was copied successfully!')
