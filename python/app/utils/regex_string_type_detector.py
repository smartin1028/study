import re
import json
import datetime
import os


def detect_string_type(text):
    """
    주어진 문자열이 XML, HTML, JSON 또는 SQL 형식인지 판별합니다.

    Args:
        text (str): 분석할 문자열

    Returns:
        str: 감지된 문자열 타입 ('XML', 'HTML', 'JSON', 'SQL', 'UNKNOWN')
    """
    # 공백 제거 및 소문자 변환하여 텍스트 정규화
    normalized_text = text.strip()

    # XML 패턴 확인
    xml_pattern = r'<\?xml.*?\?>'
    if re.search(xml_pattern, normalized_text, re.IGNORECASE):
        return 'XML'

    # HTML 패턴 확인
    html_pattern = r'<!DOCTYPE\s+html>|<html.*?>|<body.*?>|<head.*?>'
    if re.search(html_pattern, normalized_text, re.IGNORECASE):
        return 'HTML'

    # JSON 패턴 확인
    try:
        json.loads(normalized_text)
        return 'JSON'
    except json.JSONDecodeError:
        pass

    # SQL 패턴 확인
    sql_pattern = r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b'
    if re.search(sql_pattern, normalized_text, re.IGNORECASE):
        return 'SQL'

    # 태그가 있는 XML/HTML 패턴 확인 (XML 선언이나 DOCTYPE 없는 경우)
    if detect_xml_without_declaration(normalized_text):
        return 'XML'

    # 알 수 없는 형식
    return 'UNKNOWN'


def detect_xml_without_declaration(text):
    """
    XML 선언문이 없는 XML 문자열을 감지합니다.

    Args:
        text (str): 분석할 문자열

    Returns:
        bool: XML 형식일 경우 True, 아닐 경우 False
    """
    # 공백 제거 및 소문자 변환하여 텍스트 정규화
    normalized_text = text.strip()

    # 기본 태그 패턴
    tag_pattern = r'<([a-zA-Z][a-zA-Z0-9_:-]*)[^>]*>.*?</\1>'
    # 자체 닫힘 태그 패턴
    self_closing_pattern = r'<([a-zA-Z][a-zA-Z0-9_:-]*)[^>]*/>'
    # 속성 패턴
    attribute_pattern = r'<[^>]+\s+([a-zA-Z][a-zA-Z0-9_:-]*)=["|\'][^"|\']*["|\']'

    # 패턴 확인
    has_tags = re.search(tag_pattern, normalized_text, re.DOTALL) is not None
    has_self_closing = re.search(self_closing_pattern, normalized_text) is not None
    has_attributes = re.search(attribute_pattern, normalized_text) is not None

    # 태그 균형 확인
    # 여는 태그와 닫는 태그 추출
    opening_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9_:-]*)[^>/]*>', normalized_text)
    closing_tags = re.findall(r'</([a-zA-Z][a-zA-Z0-9_:-]*)>', normalized_text)
    self_closed = re.findall(r'<([a-zA-Z][a-zA-Z0-9_:-]*)[^>]*/>', normalized_text)

    # 중복 없이 태그 이름 수집
    tag_names = list(set(opening_tags + closing_tags))

    # 각 태그에 대해 여는 태그와 닫는 태그의 수 확인
    balanced = True
    for tag in tag_names:
        # 자체 닫힘 태그는 닫는 태그가 필요 없음
        tag_self_closed_count = len([t for t in self_closed if t == tag])
        tag_open_count = len([t for t in opening_tags if t == tag])
        tag_close_count = len([t for t in closing_tags if t == tag])

        # 열림 태그 수 - 자체 닫힘 태그 수 = 닫힘 태그 수여야 함
        if tag_open_count - tag_self_closed_count != tag_close_count:
            balanced = False
            break

    # XML 여부 결정 (여러 조건 고려)
    is_xml = (has_tags or has_self_closing) and balanced

    # 추가 XML 특성 확인으로 신뢰도 향상
    if has_attributes or len(tag_names) > 1:
        is_xml = is_xml and True

    return is_xml


def improved_detect_string_type(text, partial_match=True):
    """
    개선된 문자열 타입 감지 함수로, 확률 기반 방식을 사용합니다.

    Args:
        text (str): 분석할 문자열
        partial_match (bool): 부분 일치도 허용할지 여부

    Returns:
        dict: 감지 결과 (각 타입별 확률과 주요 타입)
    """
    # 공백 제거 및 정규화
    normalized_text = text.strip()

    # 각 타입별 점수 초기화
    results = {
        'XML': 0.0,
        'HTML': 0.0,
        'JSON': 0.0,
        'SQL': 0.0,
        'UNKNOWN': 0.0
    }

    # XML 선언 패턴 확인
    xml_pattern = r'<\?xml.*?\?>'
    if re.search(xml_pattern, normalized_text, re.IGNORECASE):
        results['XML'] += 0.8

    # HTML 패턴 확인
    html_pattern = r'<!DOCTYPE\s+html>|<html.*?>|<body.*?>|<head.*?>'
    if re.search(html_pattern, normalized_text, re.IGNORECASE):
        results['HTML'] += 0.8

    # 일반적인 HTML 태그 확인
    common_html_tags = r'<(div|span|p|a|img|table|tr|td|th|ul|ol|li|h[1-6]|form|input|button|script|style)[^>]*>'
    if re.search(common_html_tags, normalized_text, re.IGNORECASE):
        results['HTML'] += 0.6

    # JSON 형식 확인
    try:
        json.loads(normalized_text)
        results['JSON'] += 0.9
    except json.JSONDecodeError:
        # JSON 부분 일치 확인
        if partial_match:
            json_pattern = r'^\s*[\{\[].*[\}\]]\s*$'
            if re.search(json_pattern, normalized_text, re.DOTALL):
                results['JSON'] += 0.4

    # SQL 패턴 확인
    sql_keywords = r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|FROM|WHERE|GROUP BY|ORDER BY|HAVING|JOIN)\b'
    sql_matches = re.findall(sql_keywords, normalized_text, re.IGNORECASE)
    if sql_matches:
        # 더 많은 SQL 키워드가 있을수록 SQL일 가능성이 높음
        # results['SQL'] += min(0.1 * len(sql_matches), 0.9)
        # SQL 패턴 확인
        sql_keyword_list = {
            # 주요 DML 키워드 (높은 가중치)
            'primary': r'\b(SELECT|INSERT|UPDATE|DELETE)\b',

            # 일반적인 절 키워드 (중간 가중치)
            'clauses': r'\b(FROM|WHERE|GROUP BY|ORDER BY|HAVING)\b',

            # 조인 관련 키워드 (중간 가중치)
            'joins': r'\b(JOIN|INNER JOIN|LEFT JOIN|RIGHT JOIN|FULL JOIN)\b',

            # DDL 키워드 (낮은 가중치)
            'ddl': r'\b(CREATE|ALTER|DROP|TRUNCATE)\b',

            # 추가 SQL 표현 (낮은 가중치)
            'additional': r'\b(AS|IN|BETWEEN|LIKE|IS NULL|IS NOT NULL|AND|OR|VALUES)\b'
        }

        # 각 키워드 그룹별로 매칭 확인
        primary_matches = len(re.findall(sql_keyword_list['primary'], normalized_text, re.IGNORECASE)) * 0.3
        clause_matches = len(re.findall(sql_keyword_list['clauses'], normalized_text, re.IGNORECASE)) * 0.2
        join_matches = len(re.findall(sql_keyword_list['joins'], normalized_text, re.IGNORECASE)) * 0.2
        ddl_matches = len(re.findall(sql_keyword_list['ddl'], normalized_text, re.IGNORECASE)) * 0.15
        additional_matches = len(re.findall(sql_keyword_list['additional'], normalized_text, re.IGNORECASE)) * 0.1

        # 전체 SQL 점수 계산
        sql_score = primary_matches + clause_matches + join_matches + ddl_matches + additional_matches

        # 최대 점수는 0.9로 제한
        results['SQL'] += min(sql_score, 0.9)


    # XML 선언 없는 XML 감지 추가
    if not results['XML'] >= 0.5 and detect_xml_without_declaration(normalized_text):
        results['XML'] += 0.7

    # 가장 높은 점수를 가진 타입 결정
    max_type = max(results, key=results.get)

    # 모든 타입의 점수가 낮으면 UNKNOWN으로 설정
    if results[max_type] < 0.3:
        max_type = 'UNKNOWN'
        results['UNKNOWN'] = 0.5

    return {
        'scores': results,
        'primary_type': max_type
    }


def generate_filename_by_type(content, detected_type, default_name="file"):
    """
    감지된 콘텐츠 타입에 따라 적절한 파일 이름과 확장자를 생성합니다.

    Args:
        content (str): 원본 콘텐츠
        detected_type (str): 감지된 콘텐츠 타입
        default_name (str): 기본 파일 이름

    Returns:
        str: 생성된 파일 이름 (확장자 포함)
    """
    # 현재 시간을 파일 이름에 포함시켜 고유성 보장
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 콘텐츠에서 첫 번째 태그나 의미 있는 식별자 추출 시도
    identifier = default_name

    if detected_type == 'XML':
        # XML 루트 요소 이름 추출 시도
        root_match = re.search(r'<([a-zA-Z][a-zA-Z0-9_:-]*)[^>]*>', content)
        if root_match:
            identifier = root_match.group(1).lower()
        extension = ".xml"

    elif detected_type == 'HTML':
        # HTML의 title 추출 시도
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            identifier = re.sub(r'[^\w]', '_', title_match.group(1).lower())[:20]
        extension = ".html"

    elif detected_type == 'JSON':
        # JSON에서 첫 번째 키 추출 시도
        try:
            data = json.loads(content)
            if isinstance(data, dict) and data:
                identifier = list(data.keys())[0].lower()
        except:
            pass
        extension = ".json"

    elif detected_type == 'SQL':
        # SQL 문에서 동작 유형 추출 시도
        sql_action = re.search(r'(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)', content, re.IGNORECASE)
        if sql_action:
            identifier = sql_action.group(1).lower()
        extension = ".sql"

    else:
        # 알 수 없는 타입은 기본 텍스트 파일로 처리
        extension = ".txt"

    # 식별자가 너무 길거나 특수 문자가 있는 경우 정리
    identifier = re.sub(r'[^\w]', '_', identifier)[:20]

    # 최종 파일 이름 생성
    return f"{identifier}_{timestamp}{extension}"


def save_detected_content(content, output_dir="."):
    """
    콘텐츠 타입을 감지하고 적절한 파일 이름으로 저장합니다.

    Args:
        content (str): 저장할 콘텐츠
        output_dir (str): 출력 디렉토리

    Returns:
        tuple: (저장된 파일 경로, 감지된 타입)
    """
    # 타입 감지
    detection_result = improved_detect_string_type(content)
    detected_type = detection_result['primary_type']

    # 파일 이름 생성
    filename = generate_filename_by_type(content, detected_type)

    # 파일 저장 경로
    file_path = os.path.join(output_dir, filename)

    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return file_path, detected_type


def process_log_file(log_file_path):
    """
    로그 파일을 처리하여 구조화된 내용을 추출합니다.

    Args:
        log_file_path (str): 로그 파일 경로

    Returns:
        list: 로그 항목 목록
    """
    log_entries = []

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            current_entry = None
            content_buffer = []

            for line in f:
                # 새 로그 항목 시작 패턴 확인
                entry_start = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}) \[([^\]]+)\]', line)

                if entry_start:
                    # 이전 항목이 있으면 저장
                    if current_entry is not None and content_buffer:
                        current_entry['content'] = ''.join(content_buffer)
                        log_entries.append(current_entry)
                        content_buffer = []

                    # 새 항목 시작
                    timestamp = entry_start.group(1)
                    component = entry_start.group(2)

                    current_entry = {
                        'timestamp': timestamp,
                        'component': component,
                        'content': '',
                        'content_type': 'UNKNOWN'
                    }

                    # 첫 줄에서 내용 부분 추출
                    content_part = line[entry_start.end():].strip()
                    if content_part:
                        content_buffer.append(content_part + '\n')

                else:
                    # 현재 항목에 내용 추가
                    if current_entry is not None:
                        content_buffer.append(line)

            # 마지막 항목 처리
            if current_entry is not None and content_buffer:
                current_entry['content'] = ''.join(content_buffer)
                log_entries.append(current_entry)

    except Exception as e:
        print(f"로그 파일 처리 중 오류 발생: {e}")

    # 각 항목의 콘텐츠 타입 감지
    for entry in log_entries:
        if entry['content']:
            detection_result = improved_detect_string_type(entry['content'])
            entry['content_type'] = detection_result['primary_type']

    return log_entries


def extract_and_save_from_logs(log_file_path, output_dir="."):
    """
    로그 파일에서 구조화된 콘텐츠를 추출하여 타입별로 저장합니다.

    Args:
        log_file_path (str): 로그 파일 경로
        output_dir (str): 출력 디렉토리

    Returns:
        dict: 저장된 파일 정보
    """
    saved_files = {
        'XML': [],
        'HTML': [],
        'JSON': [],
        'SQL': [],
        'UNKNOWN': []
    }

    # 로그 파일 처리
    log_entries = process_log_file(log_file_path)

    for entry in log_entries:
        content = entry['content']
        content_type = entry['content_type']

        # 콘텐츠가 충분히 의미 있는 경우만 저장
        if len(content) > 50:  # 최소 길이 기준
            file_path, detected_type = save_detected_content(content, output_dir)
            saved_files[detected_type].append({
                'path': file_path,
                'timestamp': entry['timestamp'],
                'component': entry['component']
            })

    return saved_files


# 사용 예시
if __name__ == "__main__":
    # 예제 콘텐츠
    xml_example = """
    <root>
      <person id="1">
        <name>John Doe</name>
        <age>30</age>
        <skills>
          <skill>Python</skill>
          <skill>Data Analysis</skill>
        </skills>
      </person>
    </root>
    """

    # 타입 감지
    detected = improved_detect_string_type(xml_example)
    print(f"감지된 타입: {detected['primary_type']}")
    print(f"타입별 점수: {detected['scores']}")

    # 파일 저장
    file_path, file_type = save_detected_content(xml_example, "")
    print(f"파일 저장됨: {file_path} (타입: {file_type})")

    # 로그 파일 처리 예시
    # extract_and_save_from_logs("example_log.txt", "output_dir")
