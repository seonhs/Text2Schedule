import os
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 모듈 호출 환경(상위 폴더 및 패키지)에 대응하는 하위 호환 임포트
try:
    from src.validator import normalize_schedule_data
except ImportError:
    from validator import normalize_schedule_data

load_dotenv()

# 메타 시스템 프롬프트 파일 경로 (prompt.md)
PROMPT_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompt.md")

def load_system_prompt() -> str:
    """prompt.md 파일에서 AI 메타 시스템 프롬프트를 로드합니다."""
    if os.path.exists(PROMPT_FILE_PATH):
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "당신은 일정 정보를 추출하는 AI 분석기입니다. 문자에서 일정 정보를 추출하여 JSON 배열로 반환하세요."

def fallback_heuristic_parser(text: str, current_time: str = None) -> list[dict]:
    """
    AI API 사용이 불가능하거나 실패할 경우 정규식 규칙에 따라 기본 추출을 수행하는 Fallback 파서입니다.
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

def extract_schedule_from_text(
    text: str, 
    api_key: str | None = None, 
    model_name: str = "gemini-2.5-flash",
    received_time: str | None = None
) -> list[dict]:
    """
    Google Gemini API를 사용하여 안내 문자에서 일정 정보를 추출합니다.
    API 호출에 실패하면 정규식 기반 Fallback 파서로 자동 전환됩니다.
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        return fallback_heuristic_parser(text, received_time)

    system_prompt = load_system_prompt()
    ref_time = received_time or datetime.now().isoformat()
    
    user_prompt = f"수신 시각: {ref_time}\n메시지 본문:\n{text}"

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        # 주 모델 호출 실패 시 대체 모델 순차 시도
        models_to_try = [model_name, "gemini-2.5-flash", "gemini-3.5-flash-lite"]
        response = None
        last_err = None

        for m in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )
                if response and response.text:
                    break
            except Exception as e:
                last_err = e
                continue

        if not response or not response.text:
            raise RuntimeError(f"Gemini API 응답이 비어있습니다. 오류 내용: {last_err}")

        # AI 출력에 마크다운 코드블록(```json)이 포함된 경우 정제 처리
        raw_json_str = response.text.strip()
        if raw_json_str.startswith("```json"):
            raw_json_str = raw_json_str[7:]
        if raw_json_str.startswith("```"):
            raw_json_str = raw_json_str[3:]
        if raw_json_str.endswith("```"):
            raw_json_str = raw_json_str[:-3]

        parsed = json.loads(raw_json_str.strip())
        if not isinstance(parsed, list):
            parsed = [parsed]

        # 파싱된 JSON 객체 리스트 정규화
        normalized_list = [normalize_schedule_data(item) for item in parsed]
        return normalized_list

    except Exception as e:
        print(f"[AI 서비스 알림] Gemini API 호출 중 예외 발생 (Fallback 파서 전환): {e}")
        return fallback_heuristic_parser(text, received_time)
