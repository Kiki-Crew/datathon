from collections import defaultdict
from typing import Any, Dict, List


def classify_simple(
    papers: List[Dict[str, Any]],
    *,
    major_key: str = 'NODE_CLSS_01',
    minor_key: str = 'NODE_CLSS_02',
    default_major: str = '미분류',
    default_minor: str = '미분류',
) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """
    기본 분류: 대분류 > 중분류
    결과는 분류_기본.json 저장
    """
    classified = defaultdict(lambda: defaultdict(list))

    for paper in papers:
        major = paper.get(major_key) or default_major
        minor = paper.get(minor_key) or default_minor
        classified[major][minor].append(paper)

    return {major: dict(minors) for major, minors in classified.items()}
