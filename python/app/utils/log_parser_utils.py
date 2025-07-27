import re
from typing import List

from app.utils.xml_utils import XMLLogExtractor
from app.utils.file_utils import is_file_path

# 로그의 메시지를 구분하기 위한 패턴 정보
pattern_msg_splite = r'( : )'

# 로그의 시작 메시지를 구분하는 패펀 정보 (타임 스탬프)
start_pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

def find_log_messages(str_info):
    """
    :param str_info: 문자열 데이터
    :return: 로그 패턴으로 나눈 데이터 목록
    """
    if is_file_path(str_info):
        return find_log_messages_by_file(str_info)
    else:
        return find_log_messages_by_string(str_info)


def find_log_messages_by_file(log_file_path):
    # 로그 메시지 시작 패턴 (예: 타임스탬프로 시작하는 경우)
    messages = []
    current_message = []
    start_pos = 0

    with open(log_file_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            current_message, start_pos = get_log_data_by_line(current_message, line, line_num, messages, start_pattern, start_pos)

        # 마지막 메시지 추가
        if current_message:
            messages.append({
                'start_line': start_pos,
                'end_line': line_num,
                'content': ''.join(current_message)
            })

    return messages


def get_log_data_by_line(current_message, line, line_num, messages, start_pattern, start_pos):
    if start_pattern.match(line):
        if current_message:  # 이전 메시지 저장
            messages.append({
                'start_line': start_pos,
                'end_line': line_num - 1,
                'content': ''.join(current_message)
            })
            current_message = []
        start_pos = line_num  # 새 메시지 시작 위치
    current_message.append(line)
    return current_message, start_pos


def find_log_messages_by_string(source):
    # 로그 메시지 시작 패턴 (예: 타임스탬프로 시작하는 경우)
    messages = []
    current_message = []
    start_pos = 0

    lines = source.data_list('\n')
    for line_num, line in enumerate(lines, 1):
        current_message, start_pos = get_log_data_by_line(current_message, line, line_num, messages, start_pattern, start_pos)

    # 마지막 메시지 추가
    if current_message:
        messages.append({
            'start_line': start_pos,
            'end_line': line_num,
            'content': ''.join(current_message)
        })

    return messages



# 특정 XML 블록만 추출하여 포맷팅하는 예시
def extract_and_format_specific_xml(log_text: str, target_tag: str = None) -> List[str]:
    extractor = XMLLogExtractor()
    xml_blocks = extractor.find_xml_blocks(log_text)

    formatted_blocks = []
    for block in xml_blocks:
        if target_tag is None or block.tag == target_tag:
            formatted_blocks.append(extractor.to_xml_string(block))

    return formatted_blocks

# 특정 XML 블록만 추출하여 포맷팅하는 예시
def show_xml_single_line(log_text: str, target_tag: str = None) -> List[str]:
    extractor = XMLLogExtractor()
    xml_blocks = extractor.find_xml_blocks(log_text)

    formatted_blocks = []
    for block in xml_blocks:
        if target_tag is None or block.tag == target_tag:
            formatted_blocks.append(extractor.to_single_line_xml(block))

    return formatted_blocks

