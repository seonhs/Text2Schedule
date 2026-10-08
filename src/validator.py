import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

# 한국 표준시(KST: UTC+9) 타임존 설정
KST = timezone(timedelta(hours=9))

def format_date_iso(date_str: Any) -> Optional[str]:
    """날짜 문자열을 표준 ISO 포맷('YYYY-MM-DD')으로 변환합니다."""
    if not date_str:
        return None
    clean_date = re.sub(r'[^\d]', '', str(date_str))
    if len(clean_date) >= 8:
        year, month, day = clean_date[:4], clean_date[4:6], clean_date[6:8]
        return f"{year}-{month}-{day}"
    return None

# 하위 호환 별칭
format_date_to_iso = format_date_iso
format_date_extended = format_date_iso

def format_time_iso(time_str: Any) -> Optional[str]:
    """시간 문자열을 표준 ISO 포맷('HH:MM:SS')으로 변환합니다."""
    if not time_str:
        return None
    clean_time = re.sub(r'[^\d]', '', str(time_str))
    if len(clean_time) == 6:
        return f"{clean_time[:2]}:{clean_time[2:4]}:{clean_time[4:6]}"
    elif len(clean_time) == 4:
        return f"{clean_time[:2]}:{clean_time[2:4]}:00"
    elif ':' in str(time_str):
        parts = str(time_str).split(':')
        if len(parts) == 2:
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:00"
        elif len(parts) == 3:
            return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}:{parts[2].zfill(2)}"
    return None

# 하위 호환 별칭
format_time_to_iso = format_time_iso
format_time_extended = format_time_iso

def build_full_iso_datetime(date_iso: Any, time_iso: Any, tz_suffix: str = "+09:00") -> Optional[str]:
    """
    날짜와 시간을 표준 ISO 8601 일시 문자열('YYYY-MM-DDTHH:MM:SS+09:00')로 결합합니다.
    """
    d_str = format_date_iso(date_iso)
    if not d_str:
        return None
    t_str = format_time_iso(time_iso) or "09:00:00"
    return f"{d_str}T{t_str}{tz_suffix}"

class ScheduleItem(BaseModel):
    """
    Pydantic v2 기반 단일 표준 일정 데이터 모델.
    중복 키 없이 표준 ISO 8601 포맷 하나의 딕셔너리로 저장하고 검증합니다.
    """
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    action: str = "create"
    status: str = "CONFIRMED"
    summary: str = Field(default="일정", alias="SUMMARY")
    date: Optional[str] = Field(default=None, alias="DATE")
    start_time: Optional[str] = Field(default=None, alias="START_TIME")
    end_time: Optional[str] = Field(default=None, alias="END_TIME")
    start_iso: Optional[str] = None
    end_iso: Optional[str] = None
    location: Optional[str] = Field(default=None, alias="LOCATION")
    description: Optional[str] = Field(default=None, alias="DESCRIPTION")
    rrule: Optional[str] = Field(default=None, alias="RRULE")
    needs_review: bool = False
    review_reason: Optional[str] = None
    match_hint: Optional[dict] = None

    @model_validator(mode="before")
    @classmethod
    def validate_and_normalize(cls, data: Any) -> Any:
        """입력 데이터를 수신받아 단일 표준 형식으로 검증 및 정규화합니다."""
        if not isinstance(data, dict):
            return data

        raw_date = data.get("DATE") or data.get("date")
        raw_start = data.get("START_TIME") or data.get("start_time")
        raw_end = data.get("END_TIME") or data.get("end_time")

        date_iso = format_date_iso(raw_date)
        start_time_iso = format_time_iso(raw_start)
        end_time_iso = format_time_iso(raw_end)

        # 시작 시각은 존재하나 종료 시각이 없는 경우 +1시간 자동 설정
        if start_time_iso and not end_time_iso and date_iso:
            try:
                st_dt = datetime.strptime(f"{date_iso} {start_time_iso}", "%Y-%m-%d %H:%M:%S")
                et_dt = st_dt + timedelta(hours=1)
                end_time_iso = et_dt.strftime("%H:%M:%S")
            except ValueError:
                pass

        summary = data.get("SUMMARY") or data.get("summary") or "일정"
        location = data.get("LOCATION") or data.get("location")
        description = data.get("DESCRIPTION") or data.get("description")
        rrule = data.get("RRULE") or data.get("rrule")

        start_iso = build_full_iso_datetime(date_iso, start_time_iso)
        end_iso = build_full_iso_datetime(date_iso, end_time_iso)

        return {
            "action": data.get("action", "create"),
            "status": data.get("status", "CONFIRMED"),
            "summary": summary,
            "date": date_iso,
            "start_time": start_time_iso,
            "end_time": end_time_iso,
            "start_iso": start_iso,
            "end_iso": end_iso,
            "location": location,
            "description": description,
            "rrule": rrule,
            "needs_review": bool(data.get("needs_review", False)),
            "review_reason": data.get("review_reason"),
            "match_hint": data.get("match_hint")
        }

def normalize_schedule_data(raw_item: dict) -> dict:
    """단일 표준 형식(Pydantic ScheduleItem)으로 데이터 검증 및 정규화를 수행한 딕셔너리를 반환합니다."""
    schedule = ScheduleItem.model_validate(raw_item)
    return schedule.model_dump()
