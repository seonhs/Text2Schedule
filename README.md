📅 Text2Schedule
AI 기반 안내 문자 ➔ 캘린더 일정 변환 자동화 도구

Text2Schedule은 교육, 행사, 프로그램 등의 안내 문자 메시지(SMS, 카카오톡 등)를 입력받아 Gemini API로 분석한 뒤, 캘린더 앱에 등록할 수 있는 표준 일정 데이터(.json, .ics)로 자동 변환해 주는 Python 프로그램입니다.

복잡한 문자 내용에서 제목, 날짜, 시간, 장소, 유의사항만 빠르게 추출하여 캘린더 등록 과정을 단축시켜 줍니다.

🌟 주요 기능
🤖 AI 일정 정보 추출: 수신된 안내 문자를 분석하여 핵심 일정 항목(제목, 날짜, 시작/종료 시간, 장소, 메모)을 자동 분류

⚠️ 스마트 검토 시스템 (needs_review): 수신 시각 미제공으로 연도 추정이 필요하거나 정보가 불명확한 경우 사용자에게 주의/검토 알림

📄 표준 ICS 파일 생성: 추출된 일정 정보를 Android 삼성 캘린더, Google Calendar 등에서 바로 등록 가능한 .ics 형식으로 변환

🔄 반복 및 일정 변경 감지: 동일 문자 내 다중 일정 및 변경/취소 안내 유형(create, update, cancel) 구분

🔒 개인정보 보호: API Key 환경변수 분리 및 필수 일정 데이터 외 불필요한 개인 식별 정보 처리 지양

🚀 빠른 시작 (Quick Start)
1. 사전 준비 (Prerequisites)
Python 3.10 이상

Google Gemini API Key (Google AI Studio에서 발급 가능)

2. 설치 (Installation)
저장소를 클론하고 필요한 라이브러리를 설치합니다.

Bash
# 저장소 클론
git clone https://github.com/your-username/Text2Schedule.git
cd Text2Schedule

# 필수 라이브러리 설치
pip install google-genai python-dotenv
3. 환경 변수 설정 (Environment Setup)
프로젝트 루트 디렉터리에 .env 파일을 생성하고 발급받은 Gemini API 키를 작성합니다.

코드 스니펫
GEMINI_API_KEY=your_gemini_api_key_here
⚠️ 주의: .env 파일은 개인 API 키가 포함되므로 Git 저장소에 커밋되지 않도록 .gitignore에 등록되어 있습니다.

💻 사용 방법 (Usage)
기본 실행
main.py를 실행하면 대화형 모드로 전환되어 분석할 텍스트 파일 경로를 직접 입력받습니다.

Bash
python main.py
인자(Argument) 지정 실행
입력 파일 및 출력 경로를 옵션 인자로 전달하여 실행할 수 있습니다.

Bash
# 특정 문자 텍스트 파일 분석
python main.py data/samples/sample_msg.txt

# 출력 JSON 파일명 지정 및 모델 변경
python main.py data/samples/sample_msg.txt -o my_schedule.json --model gemini-3.1-flash-lite
📂 데이터 처리 예시
1. 입력 (안내 문자 텍스트)
Plaintext
[Web발신]
[프로그램 안내- 청년일자리스테이션]

신청하신 <필승!말빨연구소> 프로그램이 월요일 진행됩니다!

- 일정: 8월 24일(월)
- 시간: 10:00 ~ 13:00
- 장소: 청년일자리스테이션
※ 현장 주차 공간이 매우 협소하며 유료로 운영됩니다.
- 필수! 확인사항 -
1. 고용24 구직신청 및 확인증 제출 필수 (gjrepi2@naver.com)
2. 당일 취소 및 노쇼 불가
2. 출력 (JSON 결과)
JSON
[
  {
    "action": "create",
    "SUMMARY": "필승!말빨연구소",
    "DATE": "20260824",
    "START_TIME": "100000",
    "END_TIME": "130000",
    "LOCATION": "청년일자리스테이션",
    "RRULE": null,
    "DESCRIPTION": "현장 주차 공간 협소. 고용24 구직신청 및 확인증 제출 필수 (gjrepi2@naver.com). 당일 취소 및 노쇼 불가.",
    "needs_review": true,
    "review_reason": "수신 시각 정보가 없어 8월 24일이 월요일인 2026년으로 연도를 추정하였습니다.",
    "match_hint": null
  }
]
3. 캘린더 등록
생성된 .ics 파일을 스마트폰(Android 삼성 캘린더 등)으로 전달하여 실행하면 한 번의 터치로 일정이 등록됩니다.

📁 프로젝트 구조
Plaintext
Text2Schedule/
├── main.py                # CLI 실행 및 전체 분석 파이프라인
├── prompt.md              # Gemini API 메타 시스템 프롬프트
├── PROJECT.md             # 프로젝트 세부 명세 및 기술 개발 문서
├── README.md              # 프로젝트 안내 문서 (본 파일)
├── .env                   # API KEY 환경변수 파일 (Git 미포함)
├── .gitignore             # Git 제외 파일 목록
├── data/
│   └── samples/           # 테스트용 문자 샘플 파일
└── tests/                 # 파이프라인 단위 테스트
🛠️ 개발 로드맵 (Roadmap)
[x] Phase 1: .ics 캘린더 파일 생성 및 삼성 캘린더 연동 검증

[x] Phase 2: Python 프로젝트 기본 구조 및 CLI 환경 구축

[x] Phase 3: Gemini API 기반 일정 정보 JSON 추출 엔진 구현

[ ] Phase 4: 추출된 일정 검토 및 수정을 위한 사용자 승인 UI 개발

[ ] Phase 5: 동일 문자의 다중 일정 분리 및 일정 변경/취소 매칭 기능 강화

[ ] Phase 6: Android 공유하기(Intent) 연동 전용 모바일 앱 확장

📄 라이선스 (License)
이 프로젝트는 MIT License에 따라 자유롭게 수정 및 재배포가 가능합니다. Detailed spec & architecture 정보는 PROJECT.md를 참고해 주세요.