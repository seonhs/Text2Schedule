# 📅 Text2Schedule

> **AI 기반 안내 문자 ➔ 단일 표준 ISO 8601 JSON & 스마트폰 캘린더(.ics) 자동 변환 도구**

Text2Schedule은 교육, 행사, 프로그램 등의 안내 문자 메시지(SMS, 카카오톡 등)를 입력받아 **Google Gemini API**로 분석한 뒤, Pydantic v2 모델 검증을 거쳐 단일 표준 ISO 8601 JSON 데이터 및 스마트폰 캘린더 등록용 경량화 `.ics` 파일로 자동 변환해 주는 Python 애플리케이션입니다.

---

## 💡 프로젝트 배경 및 해결하는 문제 (Background & Problem)

### 1. 배경 (Background)
기관이나 교육 시설에서는 일정, 장소 변경, 준비사항 등을 문자 메시지나 카카오톡으로 전달하는 경우가 많습니다. 문자는 확인하기에 편리하지만, 사용자가 캘린더 앱에 **제목, 날짜, 시간, 장소, 메모**를 일일이 직접 확인하고 다시 입력해야 하는 번거로움이 있습니다.

### 2. 해결하려는 문제 (Problem)
기존 일정 등록 방식:
> 문자 확인 ➔ 날짜/시간 확인 ➔ 캘린더 앱 실행 ➔ 제목 입력 ➔ 날짜 입력 ➔ 시간 입력 ➔ 장소 입력 ➔ 메모 입력 ➔ 저장 (반복 및 누락 가능성 존재)

**Text2Schedule의 개선된 흐름**:
> **문자 복사 ➔ Text2Schedule 입력 ➔ AI 자동 분석 ➔ ISO JSON 확인 ➔ .ics 다운로드 ➔ 원터치 캘린더 등록**

---

## 🌟 주요 기능 (Key Features)

- 🤖 **AI 기반 일정 정보 추출**: 수신된 안내 문자를 분석하여 핵심 일정 항목(제목, 날짜, 시간, 장소, 유의사항)을 자동 분류 및 추출 (`prompt.md`)
- 🛡️ **Pydantic v2 단일 표준 검증**: 중복 필드 없이 일관된 단일 표준 ISO 8601 포맷으로 검증 및 정규화 (`src/validator.py`)
- 📄 **스마트폰 캘린더(.ics) 자동 생성**: 삼성 갤럭시 캘린더, 구글 캘린더 등에서 원터치로 즉시 등록 가능한 경량 `.ics` 형식 생성 (`src/ics_calendar.py`)
- 📱 **모바일 / 웹 UI 지원**: 스마트폰 브라우저나 PC에서 문자를 복사/붙여넣기하여 즉시 ISO JSON 확인 및 `.ics` 파일 다운로드 (`app.py`)
- ⚙️ **오프라인 Fallback 지원**: API 키 미설정 또는 네트워크 장애 시 정규식 패턴 기반 기본 추출 기능 제공 (`src/fallback_parser.py`)
- 🧪 **단위 테스트 검증**: PyUnit 기반 전체 파이프라인 및 모듈 단위 테스트 내장 (`tests/test_schedule.py`)

---

## 🚀 빠른 시작 (Quick Start)

### 1. 사전 준비 (Prerequisites)
- Python 3.10 이상
- Google Gemini API Key ([Google AI Studio](https://aistudio.google.com/)에서 발급 가능)

### 2. 설치 (Installation)
필수 라이브러리를 설치합니다.
```bash
pip install google-genai pydantic python-dotenv
```

### 3. 환경 변수 설정 (Environment Setup)
프로젝트 루트 디렉터리에 `.env` 파일을 생성하고 발급받은 Gemini API 키를 작성합니다.
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 💻 사용 방법 (Usage)

### 1. CLI 터미널 실행
```bash
# 샘플 문자 파일 분석 실행
python main.py data/samples/sample_msg.txt

# 대화형 직접 입력 실행 (문자 복사 후 Ctrl+Z + Enter)
python main.py
```

### 2. 모바일 / 웹 UI 실행 (스마트폰 메시지 입력용)
```bash
python app.py
# 또는
python main.py --web
```
- 실행 시 출력되는 모바일 접속 주소(예: `http://192.168.X.X:8000`)를 스마트폰 브라우저(크롬, 삼성 인터넷 등)에 입력합니다.
- 휴대폰 문자를 복사하여 붙여넣고 **`⚡ AI 일정 분석 및 ISO 변환`** 클릭 후 **`.ics 다운로드`**를 터치하여 캘린더에 즉시 등록합니다.

### 3. 단위 테스트 실행
```bash
python -m unittest discover -s tests
```

---

## 📂 데이터 처리 예시 (Data Example)

### 1. 입력 (안내 문자 텍스트: `data/samples/sample_msg.txt`)
```text
[Web발신]
[프로그램 안내- 청년일자리스테이션]

신청하신 <필승!말빨연구소> 프로그램이 월요일 진행됩니다!

- 일정: 8월 24일(월)
- 시간: 10:00 ~ 13:00
- 장소: 청년일자리스테이션
※ 현장 주차 공간이 매우 협소하며 유료로 운영됩니다.
- 필수! 확인사항 -
1. 고용24 구직신청 및 확인증 제출 필수
2. 당일 취소 및 노쇼 불가
```

### 2. 출력 (단일 표준 ISO 8601 JSON: `schedule_iso.json`)
```json
[
  {
    "action": "create",
    "status": "CONFIRMED",
    "summary": "필승!말빨연구소",
    "date": "2026-08-24",
    "start_time": "10:00:00",
    "end_time": "13:00:00",
    "start_iso": "2026-08-24T10:00:00+09:00",
    "end_iso": "2026-08-24T13:00:00+09:00",
    "location": "청년일자리스테이션",
    "description": "1. 고용24 구직신청 및 확인증 제출 필수\n2. 당일 취소 및 노쇼 불가",
    "rrule": null,
    "needs_review": false,
    "review_reason": null,
    "match_hint": null
  }
]
```

### 3. 출력 (경량 .ics 캘린더 파일: `schedule.ics`)
```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//GALAXY CALENDAR//Calendar//EN
BEGIN:VEVENT
UID:20261008T032640Z-1@GALAXY-CALENDAR-EVENT-3a9b1c
DTSTAMP:20261008T032640Z
DESCRIPTION:1. 고용24 구직신청 및 확인증 제출 필수\n2. 당일 취소 및 노쇼 불가
SUMMARY:필승!말빨연구소
LOCATION:청년일자리스테이션
DTSTART;TZID=Asia/Seoul:20260824T100000
DTEND;TZID=Asia/Seoul:20260824T130000
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR
```

---

## 🛠️ 단계별 개발 로드맵 (Roadmap)

- [x] **Phase 1**: 경량 .ics 캘린더 파일 생성 및 갤럭시 캘린더 연동 검증
- [x] **Phase 2**: Python 프로젝트 기본 구조 및 CLI 환경 구축
- [x] **Phase 3**: Gemini API 기반 일정 정보 JSON 추출 및 Pydantic v2 정규화 구현
- [x] **Phase 4**: 스마트폰 접속 지원 반응형 모바일 웹 UI (`app.py`) 개발
- [ ] **Phase 5**: 동일 문자 내 다중 일정 분리 및 일정 변경/취소 감지 매칭 강화
- [ ] **Phase 6**: Android 공유하기(Intent) 및 SMS 자동 수신 연동 모바일 앱 확장

---

## 📁 프로젝트 구조 (Project Structure)

```text
Text2Schedule/
├── main.py                # CLI 실행 및 모바일 웹 UI 구동 메인 진입점
├── app.py                 # 모바일 반응형 웹 UI 및 HTTP API 서버
├── prompt.md              # AI 일정 추출 메타 시스템 프롬프트
├── README.md              # 프로젝트 종합 가이드 문서 (본 파일)
├── requirements.txt       # 필수 파이썬 패키지 목록
├── .env                   # GEMINI_API_KEY 환경변수 설정 파일
├── src/
│   ├── main.py            # CLI 보조 진입점
│   ├── parser.py          # AI 분석 + ICS 생성 파이프라인
│   ├── ai_service.py      # Gemini API 연동 모듈
│   ├── fallback_parser.py # API 장애 시 정규식 기반 Fallback 추출 파서
│   ├── validator.py       # Pydantic v2 기반 단일 표준 검증/정규화
│   └── ics_calendar.py    # 갤럭시 캘린더 규격 경량 .ics 생성기
├── data/
│   └── samples/
│       ├── sample_msg.txt # 입력 테스트용 샘플 문자 파일
│       └── sample_msg.ics # 레퍼런스 ICS 파일
└── tests/
    └── test_schedule.py   # 파이프라인 및 모듈 단위 테스트
```

---

## 📄 라이선스 (License)

이 프로젝트는 [MIT License](LICENSE)에 따라 자유롭게 수정 및 재배포가 가능합니다.