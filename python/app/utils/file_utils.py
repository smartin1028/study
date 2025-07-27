import re
import os

def has_file_extension(input_string):
    # 마지막 점 이후에 1-5자의 알파벳/숫자가 있는지 확인
    return bool(re.search(r'\.[a-zA-Z0-9]{1,5}$', input_string))


def is_file_path(input_string):
    return os.path.isfile(input_string)
#
# # 사용 예시
# print(is_file_path("/path/to/file.txt"))  # 실제 파일이 존재하면 True
# print(is_file_path("not_a_file.txt"))     # False