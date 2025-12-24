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
        # {"NODE_ID":"...", ...} 형태의 객체 추출
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


def classify_papers_from_list(papers):
    """논문 리스트를 대분류/중분류로 분류합니다."""
    
    if not papers:
        return None
    
    print(f"\n🔍 {len(papers)}편의 논문 분류 중...")
    
    classified = defaultdict(lambda: defaultdict(list))
    
    for paper in papers:
        major = paper.get('NODE_CLSS_01', '미분류')
        minor = paper.get('NODE_CLSS_02', '미분류')
        classified[major][minor].append(paper)
    
    # defaultdict를 일반 dict로 변환
    classified = {k: dict(v) for k, v in classified.items()}
    
    return classified


def print_classification(classified):
    """분류 결과를 트리 형태로 출력합니다."""
    
    print("\n" + "="*60)
    print("📊 논문 분류 결과")
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


def save_classification(classified, output_path='분류된_논문.json'):
    """분류 결과를 JSON 파일로 저장합니다."""
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(classified, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 결과를 '{output_path}' 파일로 저장했습니다.")
        return True
    except Exception as e:
        print(f"\n❌ 저장 실패: {e}")
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
    print("🔧 손상된 JSON 파일 복구 및 분류 프로그램")
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
        
        # 3. 분류 실행
        classified = classify_papers_from_list(papers)
        
        if classified:
            # 4. 결과 출력
            print_classification(classified)
            
            # 5. 결과 저장
            save_classification(classified)
            
            print("\n" + "="*60)
            print("✅ 완료!")
            print("="*60)
        else:
            print("\n❌ 분류 실패")