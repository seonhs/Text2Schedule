import argparse
import sys
import os
import json

# Windows 콘솔 출력 표준 인코딩 설정 (한글 윈도우 지원)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.parser import process_text_input

def main():
    """CLI 진입점: 입력 옵션 파싱 및 프로그램 전체 흐름 제어"""
    parser = argparse.ArgumentParser(description="Text2Schedule: 안내 문자를 ISO 8601 일정 JSON 및 ICS 파일로 자동 변환")
    parser.add_argument("input_file", nargs="?", help="분석할 문자 텍스트 파일 경로")
    parser.add_argument("-o", "--output", help="출력 JSON 파일 경로 (기본값: schedule_iso.json)", default="schedule_iso.json")
    parser.add_argument("--ics", help="출력 ICS 파일 경로 (기본값: schedule.ics)", default="schedule.ics")
    parser.add_argument("--model", help="Gemini 모델명 (기본값: gemini-2.5-flash)", default="gemini-2.5-flash")
    parser.add_argument("--web", action="store_true", help="모바일/웹 UI 서버 실행 (기본 포트 8000)")
    parser.add_argument("--port", type=int, default=8000, help="웹 서버 포트 번호")

    args = parser.parse_args()

    # 웹 서버 옵션(--web)이 지정된 경우 웹 UI 서버 실행
    if args.web:
        print(f"모바일/웹 UI 서버를 실행합니다... (http://localhost:{args.port})")
        from app import run_web_server
        run_web_server(port=args.port)
        return

    input_text = ""
    # 인자로 입력 파일이 들어온 경우 파일 내용을 읽어옴
    if args.input_file:
        if os.path.exists(args.input_file):
            with open(args.input_file, "r", encoding="utf-8") as f:
                input_text = f.read()
        else:
            print(f"[!] 파일을 찾을 수 없습니다: {args.input_file}")
            sys.exit(1)
    else:
        # 파일 경로가 없으면 직접 표준 입력(STDIN) 대화형 모드로 전환
        print("===== [Text2Schedule] 일정 문자 -> ISO JSON / ICS 변환기 =====")
        print("안내 문자 메시지 본문을 입력하세요 (입력 종료 시 Ctrl+D [Windows: Ctrl+Z 후 Enter]):\n")
        try:
            input_text = sys.stdin.read()
        except KeyboardInterrupt:
            print("\n취소되었습니다.")
            sys.exit(0)

    if not input_text.strip():
        print("[!] 입력된 내용이 없습니다.")
        sys.exit(1)

    print("\n[*] AI가 일정 정보 분석 및 ISO 8601 포맷 변환을 진행 중입니다...")
    schedules, ics_content = process_text_input(
        input_text=input_text,
        output_json_path=args.output,
        output_ics_path=args.ics,
        model_name=args.model
    )

    print("\n[OK] [ISO 8601 일정 JSON 결과]")
    print(json.dumps(schedules, ensure_ascii=False, indent=2))

    print(f"\n[+] ISO JSON 저장 완료: {os.path.abspath(args.output)}")
    print(f"[+] ICS 캘린더 저장 완료: {os.path.abspath(args.ics)}")
    print("\nTip: 스마트폰 삼성 캘린더/구글 캘린더에서 생성된 .ics 파일을 열면 즉시 일정으로 입력됩니다.")

if __name__ == "__main__":
    main()
