import re
from datetime import datetime
import json
from pathlib import Path


def parse_message(file_path):
    """텍스트 파일에서 일정 정보를 추출하여 JSON 데이터로 반환"""

    message = Path(file_path).read_text(encoding="utf-8")

    days = []
    year = 2026 # 향후 시스템 연도로 변경해야 함
    start_time = None # 시작 시간
    end_time = None # 종료 시간
    description_parts = [] # 메모

    # ================================================
    # 1. 제목 추출
    # ================================================

    # <파이썬 수업> 형식:
    title_match = re.search(r"<([^>]+)>", message)
    
    if title_match:
        title = title_match.group(1).strip()
    else:
        #  ▶프로그램명: 파이썬 수업 형식:
        title_match = re.search(r"▶\s*프로그램명:\s*(.+)", message)
        title = title_match.group(1).strip()

    # ================================================
    # 2. 날짜 추출
    # ================================================
    # - 일정: 8월 24일(월)
    # ▶일시: 8월 4일(화), 5일(수), 7일(금) 각 16:30시~20:30 (3회 필참)
    # 교육일정: 7. 28.(화), 29.(수), 30.(목) 09:30~12:30
    date_match = re.search(
        r"\s*(\d{1,2}월\s*\d{1,2}일|\d{1,2}/\d{1,2}|\d{1,2}\.\s*\d{1,2}\.)",
        message
    )

    if date_match:
        date_text = date_match.group(1)

        if "월" in date_text:
            month, day = map(
                int,
                re.findall(r"\d+", date_text)
            )

        elif "/" in date_text:
            month, day = map(
                int,
                date_text.split("/")
            )
        
        elif "." in date_text:
            month, day = map(
                int,
                re.findall(r"\d+", date_text)
            )

    # 다중 일정
    #else:
    #    month = int(date_match.group(1))
    #    first_day = int(date_match.group(2))
    #    second_day = int(date_match.group(3))
    #    third_day = int(date_match.group(4))
    #    days = [first_day, second_day, third_day]

    # ===============================================
    # 3. 시작/종료 시간 추출
    # ================================================
    
    # 10:00 ~ 13:00, 14:00 ~, 16:30시~20:30 
    time_match = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s*시?\s*~\s*(\d{1,2})(?::(\d{2}))?\s*시?",
        message
    )

    if time_match:
        start_hour = int(time_match.group(1))
        start_minute = int(time_match.group(2) or 0)

        if time_match.group(3):
            end_hour = int(time_match.group(3))
            end_minute = int(time_match.group(4) or 0)
        else:
            end_hour = start_hour + 1
            end_minute = start_minute
            description_parts.append("종료시간 확인 필요")
    
    # ==============================================
    # 4. datetime으로 변환
    # ==============================================
    start_datetime = datetime(
        year,
        month,
        day,
        start_hour,
        start_minute
    )

    if end_time:
        end_hour, end_minute = map(int, end_time.split(":"))
    else:
        end_hour = start_hour + 1
        end_minute = start_minute
        description_parts.append("종료시간 확인 필요")

    end_datetime = datetime(
        2026,
        month,
        day,
        end_hour,
        end_minute
    )

    # ================================================
    # 3. 장소 추출
    # ================================================
    # 향후 지도 정보도 추가 예정
    # 주소: 서구 상무중앙로 9, 동양빌딩 9층
    location_match = re.search(
        r"(?:장소|주소):\s*(.+)",
        message
    )

    location = (
        location_match.group(1).strip()
        if location_match
        else None
    )

    # =================================================
    # 5. 설명 / 메모 추출
    # =================================================

    # 필수상항
    # 1. 고용24 구직신청(필수)
    description_match = re.search(
        r"(.*)\s*\(필수\)$",
        message,
        re.MULTILINE
    )

    if description_match:
        description_text = description_match.group(1)
        description_parts.append(description_text)

    # ▶준비물: 개인노트북 지참(사전 요청시 대여 가능)
    description_match = re.search(
        r"준비물:\s*(.*)",
        message,
    )

    if description_match:
        description_text = description_match.group(1)
        description_parts.append(description_text)

    description = (
        "\n".join(description_parts)
        if description_parts
        else None
    )

    # ==================================================
    # 6. JSON 데이터 생성
    # ==================================================
    event = {
        "SUMMARY": title,
        "DATE": start_datetime.strftime("%Y%m%d"),
        "START_TIME": start_datetime.strftime("%H%M%S"),
        "END_TIME": end_datetime.strftime("%H%M%S"),
        "LOCATION": location,
        "DESCRIPTION": description
    }

    return event


def main():

    print("=" * 50)
    print("Text2Schedule - 문자 → JSON 변환")
    print("=" * 50)

    # 파일명 입력
    file_name = input(
        "\n텍스트 파일명을 입력하세요: "
    ).strip()

    file_path = Path(file_name)

    # 파일 존재 여부 확인
    if not file_path.exists():
        print(f"\n❌ 파일을 찾을 수 없습니다: {file_name}")
        return

    # 파일 변환
    try:
        event = parse_message(file_path)

    except UnicodeDecodeError:
        print("\n❌ 파일 인코딩을 읽을 수 없습니다.")
        print("UTF-8 형식의 텍스트 파일을 사용해주세요.")
        return

    except Exception as e:
        print(f"\n❌ 파일 처리 중 오류가 발생했습니다: {e}")
        return

    # JSON 출력
    print("\n[변환 결과]")
    print(json.dumps(
        event,
        ensure_ascii=False,
        indent=4
    ))

    # JSON 파일 저장
    output_path = file_path.with_suffix(".json")

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            event,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"\n✅ JSON 파일이 생성되었습니다.")
    print(f"📄 파일: {output_path}")


if __name__ == "__main__":
    main()