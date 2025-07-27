import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class XMLElement:
    tag: str
    attributes: Dict[str, str]
    content: Optional[str]
    children: List['XMLElement']
    raw_text: str
    start_pos: int
    end_pos: int
    has_declaration: bool = False
    declaration_text: str = ""


class XMLLogExtractor:
    def __init__(self):
        self.xml_declaration_pattern = re.compile(r'(<\?xml[^>]+\?>)')
        self.tag_pattern = re.compile(
            r'(?:(<\?xml[^>]+\?>)\s*)?\s*<([a-zA-Z][a-zA-Z0-9]*)((?:\s+[a-zA-Z][a-zA-Z0-9]*="[^"]*")*)[^>]*>(.*?)</\2>',
            re.DOTALL
        )
        self.attr_pattern = re.compile(r'([a-zA-Z][a-zA-Z0-9]*)="([^"]*)"')

    def extract_attributes(self, attr_string: str) -> Dict[str, str]:
        return dict(self.attr_pattern.findall(attr_string))

    def find_xml_blocks(self, log_text: str) -> List[XMLElement]:
        results = []
        position = 0

        while position < len(log_text):
            match = self.tag_pattern.search(log_text, position)
            if not match:
                break

            declaration_text = match.group(1) or ""
            tag = match.group(2)
            attrs = self.extract_attributes(match.group(3))
            content = match.group(4).strip()

            # 중첩된 XML 처리
            children = self.find_xml_blocks(content)

            # 자식 요소가 있는 경우 순수 콘텐츠 추출
            if children:
                for child in children:
                    content = content.replace(child.raw_text, '').strip()

            element = XMLElement(
                tag=tag,
                attributes=attrs,
                content=content if content else None,
                children=children,
                raw_text=match.group(0),
                start_pos=match.start(),
                end_pos=match.end(),
                has_declaration=bool(declaration_text),
                declaration_text=declaration_text
            )
            results.append(element)
            position = match.end()

        return results

    def to_xml_string(self, element: XMLElement, indent_level: int = 0, indent_char: str = "    ") -> str:
        """XML 요소를 문자열로 변환"""
        lines = []
        indent = indent_char * indent_level

        # XML 선언부 추가
        if element.has_declaration and indent_level == 0:
            lines.append(element.declaration_text)

        # 시작 태그 생성
        tag_start = f"{indent}<{element.tag}"

        # 속성 추가
        if element.attributes:
            attributes = ' '.join(f'{k}="{v}"' for k, v in element.attributes.items())
            tag_start += f" {attributes}"

        # 내용이나 자식이 없는 경우 self-closing 태그 사용
        if not element.content and not element.children:
            lines.append(f"{tag_start}/>")
            return '\n'.join(lines)

        lines.append(f"{tag_start}>")

        # 자식 요소 추가
        if element.children:
            for child in element.children:
                lines.append(self.to_xml_string(child, indent_level + 1, indent_char))

        # 내용 추가
        if element.content:
            content_indent = indent_char * (indent_level + 1)
            lines.append(f"{content_indent}{element.content}")

        # 닫는 태그 추가
        lines.append(f"{indent}</{element.tag}>")

        return '\n'.join(lines)

    def format_xml(self, xml_string: str) -> str:
        """XML 문자열을 파싱하고 다시 포맷팅"""
        blocks = self.find_xml_blocks(xml_string)
        return '\n'.join(self.to_xml_string(block) for block in blocks)

    def to_single_line_xml(self, element: XMLElement) -> str:
        """XML 요소를 한 줄의 문자열로 변환"""
        parts = []

        # XML 선언부 추가
        if element.has_declaration:
            parts.append(element.declaration_text)

        # 시작 태그 생성
        tag_start = f"<{element.tag}"

        # 속성 추가
        if element.attributes:
            attributes = ' '.join(f'{k}="{v}"' for k, v in element.attributes.items())
            tag_start += f" {attributes}"

        # 내용이나 자식이 없는 경우 self-closing 태그 사용
        if not element.content and not element.children:
            parts.append(f"{tag_start}/>")
            return ''.join(parts)

        parts.append(f"{tag_start}>")

        # 자식 요소 추가
        if element.children:
            for child in element.children:
                parts.append(self.to_single_line_xml(child))

        # 내용 추가
        if element.content:
            parts.append(element.content)

        # 닫는 태그 추가
        parts.append(f"</{element.tag}>")

        return ''.join(parts)

# 특정 XML 블록만 추출하여 포맷팅하는 예시
def extract_and_format_specific_xml(log_text: str, target_tag: str = None) -> List[str]:
    extractor = XMLLogExtractor()
    xml_blocks = extractor.find_xml_blocks(log_text)

    formatted_blocks = []
    for block in xml_blocks:
        if target_tag is None or block.tag == target_tag:
            formatted_blocks.append(extractor.to_xml_string(block))

    return formatted_blocks
