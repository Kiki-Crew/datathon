# common_io.py
import json
import re
from typing import Any, Dict, List

_CONTROL_CHARS_RE = re.compile(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]')


def extract_papers_from_corrupted_json(file_path: str) -> List[Dict[str, Any]]:
    """
    손상된 JSON 파일에서 논문 데이터를 추출
    정규식을 사용하여 {"NODE_ID": "...", ...} 객체를 개별 파싱!
    """
    print("손상된 파일에서 데이터 복구 중...")

    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        text = content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return []

    pattern = r'\{"NODE_ID"\s*:\s*"[^"]+".+?\}'
    matches = re.finditer(pattern, text, re.DOTALL)

    papers: List[Dict[str, Any]] = []
    success_count = 0
    fail_count = 0

    print(" - 논문 객체 추출 중...")
    for m in matches:
        try:
            paper_text = m.group(0)
            paper_text = _CONTROL_CHARS_RE.sub('', paper_text)
            paper = json.loads(paper_text, strict=False)
            if isinstance(paper, dict):
                papers.append(paper)
                success_count += 1
            else:
                fail_count += 1
        except Exception:
            fail_count += 1
            continue

    print(f"성공: {success_count}개 논문 추출")
    if fail_count:
        print(f"실패: {fail_count}개 객체 손상")

    return papers


def save_json(obj: Any, output_path: str, *, indent: int = 2) -> bool:
    """공통 JSON 저장 함수"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=indent)
        print(f"저장: {output_path}")
        return True
    except Exception as e:
        print(f"저장 실패({output_path}): {e}")
        return False


def save_papers_list(papers: List[Dict[str, Any]], output_path: str = '복구된_논문_리스트.json') -> bool:
    """복구된 논문 리스트를 {NODE_LIST: [...]} 형태로 저장"""
    return save_json({"NODE_LIST": papers}, output_path)
