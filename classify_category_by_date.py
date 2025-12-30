from collections import defaultdict
from typing import Any, Dict, List


def classify_by_category_and_date(
    papers: List[Dict[str, Any]],
    *,
    major_key: str = 'NODE_CLSS_01',
    minor_key: str = 'NODE_CLSS_02',
    date_key: str = 'PBSH',
    default_major: str = '미분류',
    default_minor: str = '미분류',
    default_date: str = '날짜미상',
) -> Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]]:
    """
    대분류 > 중분류 > 발행년월(PBSH) 로 분류
    결과는 분류_카테고리별_날짜.json 저장
    """
    classified = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for paper in papers:
        major = paper.get(major_key) or default_major
        minor = paper.get(minor_key) or default_minor
        date = paper.get(date_key) or default_date
        classified[major][minor][str(date)].append(paper)

    # defaultdict -> dict 변환
    result: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = {}
    for major, minors in classified.items():
        result[major] = {}
        for minor, dates in minors.items():
            result[major][minor] = dict(dates)

    return result
