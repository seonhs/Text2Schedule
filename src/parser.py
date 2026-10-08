import os
import json

# 모듈 호출 환경(상위 폴더 및 패키지)에 대응하는 하위 호환 임포트
try:
    from src.ai_service import extract_schedule_from_text
    from src.ics_calendar import generate_ics_from_schedule
except ImportError:
    from ai_service import extract_schedule_from_text
    from ics_calendar import generate_ics_from_schedule

def process_text_input(
    input_text: str, 
    output_json_path: str | None = None,
    output_ics_path: str | None = None,
    api_key: str | None = None,
    model_name: str = "gemini-2.5-flash"
) -> tuple[list[dict], str]:
    """
    입력 문자를 받아 전체 처리 파이프라인을 실행합니다:
    1. AI(Gemini)를 이용하여 문자에서 ISO 8601 일정 JSON을 추출합니다.
    2. 추출된 일정 정보로 iCalendar(.ics) 파일 내용 문자열을 생성합니다.
    3. 경로가 지정된 경우 JSON 및 ICS 결과 파일로 저장합니다.
    
    반환값: (정규화된 일정 딕셔너리 리스트, ICS 파일 내용 문자열)
    """
    schedules = extract_schedule_from_text(input_text, api_key=api_key, model_name=model_name)
    ics_content = generate_ics_from_schedule(schedules)

    # 지정된 경로에 결과 JSON 저장
    if output_json_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(schedules, f, ensure_ascii=False, indent=2)

    # 지정된 경로에 결과 .ics 저장
    if output_ics_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_ics_path)), exist_ok=True)
        with open(output_ics_path, "w", encoding="utf-8") as f:
            f.write(ics_content)

    return schedules, ics_content
