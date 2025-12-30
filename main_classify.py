from common_io import extract_papers_from_corrupted_json, save_json, save_papers_list
from classify_simple import classify_simple
from classify_category_by_date import classify_by_category_and_date
from classify_date_by_category import classify_by_date_and_category


def main() -> None:
    file_path = 'data.json'

    print("=" * 60)
    print("논문 분류 프로그램 -> 모듈 분리 실행")
    print("=" * 60)
    print(f"파일: {file_path}\n")

    # 1) 복구
    papers = extract_papers_from_corrupted_json(file_path)
    if not papers:
        print("\n XX 논문을 추출할 수 없음 XX ")
        return

    # 2) 복구 리스트 저장
    save_papers_list(papers, '복구된_논문_리스트.json')

    # 3-1) 대>중 분류
    print("\n - 중분류별 논문 분류(calssify_simple) 수행 중...")
    basic = classify_simple(papers)
    save_json(basic, '분류_중분류.json')

    # 3-2) 대>중>월
    print("\n - 카테고리별 발행년월 분류(classify_category_by_date) 수행 중...")
    cat_date = classify_by_category_and_date(papers)
    save_json(cat_date, '분류_카테고리별_날짜.json')

    # 3-3) 월>대>중
    print("\n - 날짜별 카테고리 분류(classify_date_by_category) 수행 중...")
    date_cat = classify_by_date_and_category(papers)
    save_json(date_cat, '분류_날짜별_카테고리.json')

    print("\n" + "=" * 60)
    print("모든 분류 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
