import uuid
from datetime import datetime, timezone, timedelta

# 한국 표준시(KST: UTC+9) 타임존 설정
KST = timezone(timedelta(hours=9))

def escape_ics_text(text: str | None) -> str:
    """iCalendar RFC 5545 표준 제어 문자 역슬래시, 세미콜론, 쉼표, 줄바꿈 이스케이프 처리"""
    if not text:
        return ""
    text = text.replace("\\", "\\\\")
    text = text.replace(";", "\\;")
    text = text.replace(",", "\\,")
    text = text.replace("\n", "\\n")
    return text

def iso_to_ics_dt(iso_str: str | None) -> str:
    """ISO 8601 일시 문자열(예: '2026-08-24T10:00:00+09:00')을 ICS 일시 포맷('20260824T100000')으로 변환합니다."""
    if not iso_str:
        return ""
    clean_iso = iso_str.split('+')[0].split('Z')[0]
    try:
        dt = datetime.fromisoformat(clean_iso)
        return dt.strftime("%Y%m%dT%H%M%S")
    except ValueError:
        digits = ''.join(c for c in iso_str if c.isdigit())
        if len(digits) >= 14:
            return digits[:14]
        elif len(digits) >= 8:
            return f"{digits[:8]}T090000"
        return ""

def generate_ics_from_schedule(schedules: list[dict], prod_id: str = "-//GALAXY CALENDAR//Calendar//EN") -> str:
    """
    정규화된 일정 딕셔너리 리스트를 sample_msg.ics와 호환되는 경량화된 iCalendar(.ics) 문자열로 생성합니다.
    """
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:{prod_id}",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]

    for idx, item in enumerate(schedules, 1):
        start_iso = item.get("start_iso")
        end_iso = item.get("end_iso")
        date_iso = item.get("date_iso")
        
        start_dt_str = iso_to_ics_dt(start_iso)
        end_dt_str = iso_to_ics_dt(end_iso)

        # sample_msg.ics 규격을 따르면서 UUID v4 난수를 조합하여 전 세계적 및 다중 일정 간 UID 충돌 방지
        unique_hash = uuid.uuid4().hex[:12]
        uid = f"{now_utc}-{idx}@GALAXY-CALENDAR-EVENT-{unique_hash}"

        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{now_utc}")

        description = item.get("description") or item.get("DESCRIPTION")
        if description:
            lines.append(f"DESCRIPTION:{escape_ics_text(description)}")

        summary = item.get("summary") or item.get("SUMMARY") or "일정"
        lines.append(f"SUMMARY:{escape_ics_text(summary)}")

        location = item.get("location") or item.get("LOCATION")
        if location:
            lines.append(f"LOCATION:{escape_ics_text(location)}")

        if start_dt_str:
            lines.append(f"DTSTART;TZID=Asia/Seoul:{start_dt_str}")
        elif date_iso:
            clean_date = date_iso.replace("-", "")
            lines.append(f"DTSTART;VALUE=DATE:{clean_date}")

        if end_dt_str:
            lines.append(f"DTEND;TZID=Asia/Seoul:{end_dt_str}")

        lines.append("STATUS:CONFIRMED")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    
    return "\r\n".join(lines) + "\r\n"
