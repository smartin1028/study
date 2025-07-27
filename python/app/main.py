import os

from utils.log_parser_utils import find_log_messages, show_xml_single_line
from utils.regex_string_type_detector import improved_detect_string_type
from utils.sql_utils import extract_all_sql_queries_v2
from utils.xml_utils import extract_and_format_specific_xml

if __name__ == "__main__":
    module_path = os.path.dirname(__file__)
    print(f"모듈 경로: {module_path}")

    # 사용 예시
    # log_messages = find_log_messages('./nohup-temp-02.out')

    log_messages = find_log_messages(f'{module_path}/utils/nohup-temp.out')
    # log_messages = find_log_messages('/Users/daewonlee/dev/git/repos/study_01/study/python/app/utils/nohup-temp.out')

    for msg in log_messages:
        print(f"Message from line {msg['start_line']} to {msg['end_line']}  {msg['content'][:50]} + ...")
        # print(f"Message from line {msg['start_line']} to {msg['end_line']}  {msg['content']} ")


        # 타입 감지
        detected = improved_detect_string_type(msg['content'])
        print(f"감지된 타입: [{detected['primary_type']}] 타입별 점수: [{detected['scores']}]")

        # if detected['primary_type'] == 'SQL':
        # 점수가 있으면 무조건 확인해 보기
        if detected['scores']['SQL'] >= 0.1:
            replace = msg['content']
            # replace = msg['content'].replace("\n", " ")
            # replace = re.sub(r'\s+', ' ', replace)
            print(replace)  # "Hello World Python"

            extracted_queries = extract_all_sql_queries_v2(replace)
            print(f"추출된 SQL 쿼리 수: {len(extracted_queries)}")
            for query in extracted_queries:
                print(query)
                print("-" * 50)

        if detected['scores']['XML'] >= 0.1 or detected['scores']['HTML'] >= 0.1:
            # xml 추출
            request_xmls = extract_and_format_specific_xml(msg['content'])
            for xml in request_xmls:

                print(show_xml_single_line(xml))


    # msg 추출
        # data_list = re.split(pattern_msg_splite, "".join(msg['content']), maxsplit=1)
        # for index,data in enumerate(data_list):
        #     print(f'index : {index} data : {data}')

        # print(msg['content'][:100] + "...")  # 내용 일부만 출력

