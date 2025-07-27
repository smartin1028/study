import jaydebeapi
import os


# Java 환경 변수 설정
# 전체 경로로 수정해서 작업
os.environ['JAVA_HOME'] = '/Library/Java/JavaVirtualMachines/corretto-11.0.19/Contents/Home'
os.environ['CLASSPATH'] = '/dev/bin/h2/bin/h2-2.1.210.jar'  # H2 JAR 파일의 실제 경로로 수정하세요

print(os.environ['JAVA_HOME'])
print(os.environ['CLASSPATH'])


# H2 JDBC 드라이버 경로 설정 (다운로드 필요)
h2_driver_path = "/dev/bin/h2/bin/h2-2.1.210.jar"

# 데이터베이스 연결 정보
url = "jdbc:h2:~/test"  # 파일 기반 데이터베이스 경로
user = "sa"             # 기본 사용자 이름
password = ""           # 기본 비밀번호는 빈 문자열

# 데이터베이스 연결
conn = jaydebeapi.connect(
    "org.h2.Driver",
    url,
    [user, password],
    h2_driver_path
)

# 커서 생성
cursor = conn.cursor()

try:
    # 테이블 생성 (필요한 경우)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users01 (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        age INT
    )
    """)

    # 데이터 삽입
    cursor.execute("""
    INSERT INTO users01 (name, email, age)
    VALUES (?, ?, ?)
    """, ("홍길동", "hong@example.com", 30))

    # 여러 데이터 한 번에 삽입
    users_data = [
        ("김철수", "kim@example.com", 25),
        ("이영희", "lee@example.com", 28),
        ("박민수", "park@example.com", 35)
    ]

    cursor.executemany("""
    INSERT INTO users01 (name, email, age)
    VALUES (?, ?, ?)
    """, users_data)

    # 변경사항 커밋
    conn.commit()
    print("데이터가 성공적으로 삽입되었습니다.")

    # 삽입된 데이터 확인
    cursor.execute("SELECT * FROM users01")
    results = cursor.fetchall()
    for row in results:
        print(row)

except Exception as e:
    print(f"오류 발생: {e}")
    conn.rollback()

finally:
    # 연결 종료
    cursor.close()
    conn.close()
