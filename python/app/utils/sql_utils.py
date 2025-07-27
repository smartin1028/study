import re

# 다양한 패턴을 고려한 통합 추출 함수
def extract_all_sql_queries(log_text):
    patterns = [
        # 기존 패턴
        r'Executing SQL:\s*([\s\S]*?;)',  # "Executing SQL: " 패턴
        r'SQL Query:\s*([\s\S]*?;)',  # "SQL Query: " 패턴

        # Hibernate SQL 패턴 수정
        r'org\.hibernate\.SQL\s*:\s*([\s\S]*?)(?=\n\d{4}|\Z)',  # 다음 로그 시작 또는 문자열 끝까지

        # 일반 SQL 키워드 패턴 (세미콜론 선택적)
        r'(?i)(SELECT|INSERT|UPDATE|DELETE)[\s\S]*?(?:;|\n\d{4}|\Z)'
    ]

    all_queries = []
    for pattern in patterns:
        matches = re.findall(pattern, log_text)
        all_queries.extend([match.strip() if isinstance(match, str) else match[0].strip() for match in matches])


    # 중복 제거 전 공백 정리
    cleaned_queries = []
    for query in all_queries:
        # 여러 줄의 공백을 단일 공백으로 변환
        query = ' '.join(line.strip() for line in query.splitlines())
        # 연속된 공백을 하나로
        query = ' '.join(query.split())
        cleaned_queries.append(query)

    # 중복 제거
    return list(set(cleaned_queries))


def extract_all_sql_queries_v2(log_text):
    patterns = [
        # 기존 패턴
        r'Executing SQL:\s*([\s\S]*?;)',  # "Executing SQL: " 패턴
        r'SQL Query:\s*([\s\S]*?;)',  # "SQL Query: " 패턴

        # Hibernate SQL 패턴
        r'org\.hibernate\.SQL\s*:\s*([\s\S]*?)(?=\n\d{4}|\Z)',

        # SQL 키워드 패턴 수정
        r'(?i)(?:Executing SQL:|SQL Query:|org\.hibernate\.SQL\s*:)?\s*((?:SELECT|INSERT|UPDATE|DELETE)[\s\S]*?(?:;|\n\d{4}|\Z))'
    ]

    all_queries = []
    for pattern in patterns:
        matches = re.findall(pattern, log_text)
        # 매칭된 그룹 처리 로직 개선
        for match in matches:
            if isinstance(match, tuple):
                # 여러 그룹이 매칭된 경우 비어있지 않은 마지막 그룹 사용
                query = next((m for m in reversed(match) if m.strip()), '')
            else:
                query = match

            if query.strip() and len(query.strip().split()) > 1:  # 단일 키워드만 있는 경우 제외
                all_queries.append(query.strip())

    # 중복 제거 전 공백 정리
    cleaned_queries = []
    for query in all_queries:
        # 여러 줄의 공백을 단일 공백으로 변환
        query = ' '.join(line.strip() for line in query.splitlines())
        # 연속된 공백을 하나로
        query = ' '.join(query.split())
        cleaned_queries.append(query)

    # 중복 제거하고 반환
    return list(set(cleaned_queries))
