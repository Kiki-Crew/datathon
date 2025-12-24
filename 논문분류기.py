import json
import re
from collections import defaultdict

def extract_papers_from_corrupted_json(file_path):
    """
    손상된 JSON 파일에서 논문 데이터를 추출합니다.
    정규식을 사용하여 NODE 객체를 개별적으로 파싱합니다.
    """
    
    print("📖 손상된 파일에서 데이터 복구 중...")
    
    papers = []
    
    try:
        # 바이너리로 읽고 에러 무시하며 디코딩
        with open(file_path, 'rb') as f:
            content = f.read()
        
        text = content.decode('utf-8', errors='ignore')
        
        # NODE 객체 패턴 찾기
        pattern = r'\{"NODE_ID"\s*:\s*"[^"]+".+?\}'
        
        print("🔍 논문 객체 추출 중...")
        matches = re.finditer(pattern, text, re.DOTALL)
        
        success_count = 0
        fail_count = 0
        
        for match in matches:
            try:
                paper_text = match.group(0)
                
                # 제어 문자 제거
                paper_text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', paper_text)
                
                # JSON 파싱 시도
                paper = json.loads(paper_text, strict=False)
                papers.append(paper)
                success_count += 1
                
            except Exception as e:
                fail_count += 1
                continue
        
        print(f"✓ 성공: {success_count}개 논문 추출")
        if fail_count > 0:
            print(f"⚠️  실패: {fail_count}개 객체 손상")
        
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")
        return []
    
    return papers


def format_date(pbsh):
    """발행년월을 보기 좋게 포맷팅합니다. (202106 -> 2021-06)"""
    if pbsh and len(pbsh) == 6:
        year = pbsh[:4]
        month = pbsh[4:]
        return f"{year}-{month}"
    return pbsh if pbsh else "날짜미상"


def classify_by_category(papers):
    """대분류 > 중분류 > 발행년월로 분류합니다."""
    
    classified = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for paper in papers:
        major = paper.get('NODE_CLSS_01', '미분류')
        minor = paper.get('NODE_CLSS_02', '미분류')
        date = paper.get('PBSH', '날짜미상')
        
        classified[major][minor][date].append(paper)
    
    # defaultdict를 일반 dict로 변환
    result = {}
    for major, minors in classified.items():
        result[major] = {}
        for minor, dates in minors.items():
            result[major][minor] = dict(dates)
    
    return result


def classify_by_date(papers):
    """발행년월 > 대분류 > 중분류로 분류합니다."""
    
    classified = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for paper in papers:
        date = paper.get('PBSH', '날짜미상')
        major = paper.get('NODE_CLSS_01', '미분류')
        minor = paper.get('NODE_CLSS_02', '미분류')
        
        classified[date][major][minor].append(paper)
    
    # defaultdict를 일반 dict로 변환
    result = {}
    for date, majors in classified.items():
        result[date] = {}
        for major, minors in majors.items():
            result[date][major] = dict(minors)
    
    return result


def classify_simple(papers):
    """기본 분류: 대분류 > 중분류"""
    
    classified = defaultdict(lambda: defaultdict(list))
    
    for paper in papers:
        major = paper.get('NODE_CLSS_01', '미분류')
        minor = paper.get('NODE_CLSS_02', '미분류')
        classified[major][minor].append(paper)
    
    return {k: dict(v) for k, v in classified.items()}


def print_classification_by_category(classified):
    """대분류 > 중분류 > 발행년월 분류 결과 출력"""
    
    print("\n" + "="*60)
    print("📊 논문 분류 결과 (대분류 > 중분류 > 발행년월)")
    print("="*60)
    
    total_papers = 0
    
    for major in sorted(classified.keys()):
        print(f"\n📚 {major}")
        minors = classified[major]
        minor_list = sorted(minors.items())
        
        for i, (minor, dates) in enumerate(minor_list):
            is_last_minor = (i == len(minor_list) - 1)
            minor_prefix = "└─" if is_last_minor else "├─"
            
            minor_total = sum(len(papers) for papers in dates.values())
            print(f"   {minor_prefix} {minor}: {minor_total}편")
            
            date_list = sorted(dates.items())
            for j, (date, papers) in enumerate(date_list):
                is_last_date = (j == len(date_list) - 1)
                date_indent = "    " if is_last_minor else "│   "
                date_prefix = "└─" if is_last_date else "├─"
                formatted_date = format_date(date)
                print(f"{date_indent} {date_prefix} {formatted_date}: {len(papers)}편")
                total_papers += len(papers)
    
    print(f"\n{'='*60}")
    print(f"✓ 총 {total_papers}편의 논문")
    print("="*60)


def print_classification_by_date(classified):
    """발행년월 > 대분류 > 중분류 분류 결과 출력"""
    
    print("\n" + "="*60)
    print("📊 논문 분류 결과 (발행년월 > 대분류 > 중분류)")
    print("="*60)
    
    total_papers = 0
    
    for date in sorted(classified.keys()):
        formatted_date = format_date(date)
        print(f"\n📅 {formatted_date}")
        majors = classified[date]
        major_list = sorted(majors.items())
        
        for i, (major, minors) in enumerate(major_list):
            is_last_major = (i == len(major_list) - 1)
            major_prefix = "└─" if is_last_major else "├─"
            
            major_total = sum(len(papers) for papers in minors.values())
            print(f"   {major_prefix} {major}: {major_total}편")
            
            minor_list = sorted(minors.items())
            for j, (minor, papers) in enumerate(minor_list):
                is_last_minor = (j == len(minor_list) - 1)
                minor_indent = "    " if is_last_major else "│   "
                minor_prefix = "└─" if is_last_minor else "├─"
                print(f"{minor_indent} {minor_prefix} {minor}: {len(papers)}편")
                total_papers += len(papers)
    
    print(f"\n{'='*60}")
    print(f"✓ 총 {total_papers}편의 논문")
    print("="*60)


def print_classification_simple(classified):
    """기본 분류 결과 출력"""
    
    print("\n" + "="*60)
    print("📊 논문 분류 결과 (대분류 > 중분류)")
    print("="*60)
    
    total_papers = 0
    
    for major, minors in sorted(classified.items()):
        print(f"\n📚 {major}")
        minor_items = sorted(minors.items())
        
        for i, (minor, papers) in enumerate(minor_items):
            is_last = (i == len(minor_items) - 1)
            prefix = "└─" if is_last else "├─"
            print(f"   {prefix} {minor}: {len(papers)}편")
            total_papers += len(papers)
    
    print(f"\n{'='*60}")
    print(f"✓ 총 {total_papers}편의 논문")
    print(f"✓ 대분류: {len(classified)}개")
    print(f"✓ 중분류: {sum(len(minors) for minors in classified.values())}개")
    print("="*60)


def save_classification(classified, output_path, mode="category"):
    """분류 결과를 JSON 파일로 저장합니다."""
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(classified, f, ensure_ascii=False, indent=2)
        print(f"✅ {mode} 분류 결과를 '{output_path}' 파일로 저장했습니다.")
        return True
    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        return False


def save_papers_list(papers, output_path='복구된_논문_리스트.json'):
    """복구된 논문 리스트를 저장합니다."""
    
    try:
        data = {"NODE_LIST": papers}
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ 복구된 데이터를 '{output_path}' 파일로 저장했습니다.")
        return True
    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        return False


# 메인 실행
if __name__ == "__main__":
    # 파일 경로 지정
    file_path = 'SSU_Datathon2025_공학분야_62199 (1).json'
    
    print("="*60)
    print("🔧 논문 분류 프로그램 (발행년월 기능 추가)")
    print("="*60)
    print(f"📁 파일: {file_path}\n")
    
    # 1. 손상된 파일에서 논문 추출
    papers = extract_papers_from_corrupted_json(file_path)
    
    if not papers:
        print("\n❌ 논문을 추출할 수 없습니다.")
        print("💡 다음을 시도해보세요:")
        print("   1. 파일을 다시 다운로드")
        print("   2. 다른 형식(CSV, Excel)으로 받기")
        print("   3. 데이터 제공자에게 문의")
    else:
        # 2. 복구된 논문 리스트 저장
        save_papers_list(papers)
        
        # 3-1. 기본 분류 (대분류 > 중분류)
        print("\n" + "🔍 기본 분류 수행 중...")
        classified_simple = classify_simple(papers)
        print_classification_simple(classified_simple)
        save_classification(classified_simple, '분류_기본.json', "기본")
        
        # 3-2. 카테고리별 분류 (대분류 > 중분류 > 발행년월)
        print("\n" + "🔍 카테고리별 발행년월 분류 수행 중...")
        classified_by_category = classify_by_category(papers)
        print_classification_by_category(classified_by_category)
        save_classification(classified_by_category, '분류_카테고리별_날짜.json', "카테고리별")
        
        # 3-3. 날짜별 분류 (발행년월 > 대분류 > 중분류)
        print("\n" + "🔍 날짜별 카테고리 분류 수행 중...")
        classified_by_date = classify_by_date(papers)
        print_classification_by_date(classified_by_date)
        save_classification(classified_by_date, '분류_날짜별_카테고리.json', "날짜별")
        
        print("\n" + "="*60)
        print("✅ 모든 분류 완료!")
        print("="*60)
        print("\n📂 생성된 파일:")
        print("   1. 복구된_논문_리스트.json - 복구된 전체 논문 데이터")
        print("   2. 분류_기본.json - 대분류 > 중분류")
        print("   3. 분류_카테고리별_날짜.json - 대분류 > 중분류 > 발행년월")
        print("   4. 분류_날짜별_카테고리.json - 발행년월 > 대분류 > 중분류")
        
        print("\n💡 사용 예시:")
        print(">>> classified = classify_by_category(papers)")
        print(">>> papers_2021_06 = classified['공학']['전기전자공학']['202106']")
        print(">>> print(f'{len(papers_2021_06)}편의 2021년 6월 논문')")