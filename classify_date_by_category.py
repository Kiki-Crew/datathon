from collections import defaultdict
from typing import Any, Dict, List


def classify_by_date_and_category(
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
    발행년월(PBSH) > 대분류 > 중분류 로 분류
    결과는 분류_날짜별_카테고리.json 저장
    """
    classified = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for paper in papers:
        date = paper.get(date_key) or default_date
        major = paper.get(major_key) or default_major
        minor = paper.get(minor_key) or default_minor
        classified[str(date)][major][minor].append(paper)

    # defaultdict -> dict 변환
    result: Dict[str, Dict[str, Dict[str, List[Dict[str, Any]]]]] = {}
    for date, majors in classified.items():
        result[date] = {}
        for major, minors in majors.items():
            result[date][major] = dict(minors)

    return result
