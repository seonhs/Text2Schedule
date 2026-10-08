import re
from datetime import datetime

# 모듈 호출 환경(상위 폴더 및 패키지)에 대응하는 하위 호환 임포트
try:
    from src.validator import normalize_schedule_data
except ImportError:
    from validator import normalize_schedule_data

def fallback_heuristic_parser(text: str, current_time: str = None) -> list[dict]:
    """
    AI API 사용이 불가능하거나 실패할 경우 정규식 규칙에 따라 기본 일정 정보를 추출하는 Fallback 파서 모듈입니다.
    """
    now = datetime.now()
    if current_time:
        try:
            now = datetime.fromisoformat(current_time)
        except Exception:
            pass

    # 기본 정규식 패턴 (날짜, 시간, 제목, 장소 추출)
    clean_text = re.sub(r'\[Web발신\]', '', text)
    date_match = re.search(r'(\d{1,2})월\s*(\d{1,2})일', clean_text)
    time_match = re.search(r'(\d{1,2}):(\d{2})\s*~\s*(\d{1,2}):(\d{2})', clean_text)
    title_match = re.search(r'<([^>]+)>|\[([^\]]+)\]', clean_text)
    location_match = re.search(r'장소\s*:\s*([^\n]+)', clean_text)
    
    summary = "안내 일정"
    if title_match:
        summary = title_match.group(1) or title_match.group(2) or summary

    year = now.year
    month = now.month
    day = now.day

    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))

    date_str = f"{year}{month:02d}{day:02d}"

    start_time_str = "100000"
    end_time_str = "120000"
    if time_match:
        sh, sm, eh, em = time_match.groups()
        start_time_str = f"{int(sh):02d}{sm}00"
        end_time_str = f"{int(eh):02d}{em}00"

    location_str = location_match.group(1).strip() if location_match else None

    raw_item = {
        "action": "create",
        "SUMMARY": summary,
        "DATE": date_str,
        "START_TIME": start_time_str,
        "END_TIME": end_time_str,
        "LOCATION": location_str,
        "DESCRIPTION": text[:200],
        "needs_review": True,
        "review_reason": "AI API 미연동으로 기본 규칙에 따라 변환되었습니다."
    }
    return [normalize_schedule_data(raw_item)]

