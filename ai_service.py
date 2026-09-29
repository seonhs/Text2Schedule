"""
Text2Schedule - Gemini API 기반 일정 추출 스크립트
====================================================

문자(SMS/카카오톡 등) 메시지를 입력받아 Gemini API로 분석한 뒤,
PROJECT.md에 정의된 일정 스키마에 맞춰 JSON 배열로 저장합니다.

사전 준비
---------
    pip install google-genai python-dotenv

    프로젝트 루트에 .env 파일을 만들고 아래처럼 API 키를 작성하세요.
    (PROJECT.md 9.5 개인정보 보호 원칙에 따라 .env는 .gitignore에 포함되어야 합니다)

        GEMINI_API_KEY=발급받은_API_키

사용 예
-------
    # 기본 사용 (파일명을 인자로 주지 않으면 실행 중 직접 입력)
    
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# ==================================================
# 시스템 프롬프트: docs/prompt.md 등 별도 파일에서 읽어옵니다.
# ==================================================
DEFAULT_PROMPT_PATH = Path(__file__).resolve().parent / "prompt.md"
model_name = "gemini-3.1-flash-lite" # 260922 최신 무료 모델

def load_api_key() -> str:
    """`.env` 파일에서 GEMINI_API_KEY를 읽어옵니다."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
        sys.exit(1)
    return api_key

def load_meta_prompt(prompt_path: Path) -> str:
    return prompt_path.read_text(encoding="utf-8")

def extract_schedule(
    message: str,
    meta_prompt: str,
    client,
    model_name: str,
) -> list:
    """입력받은 문자 내용을 Gemini의 응답을 JSON 일정 정보 목록으로 변환해서 반환한다."""
    
    response = client.interactions.create(
        model=model_name,
        input = f"{meta_prompt}\n{message}" 
    )
    print("\n[Gemini 원본 응답]")
    print(response.output_text)
    
    try:
        events = json.loads(response.output_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemini 응답을 JSON으로 파싱할 수 없습니다.\n"
            f"원본 응답:\n{response.output_text}"
        ) from e

    if not isinstance(events, list):
        raise ValueError("Gemini 응답이 JSON 배열이 아닙니다.")
    
    return events


def save_events(events: list, output_path: Path) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Text2Schedule - Gemini 일정 추출기")
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="분석할 문자 메시지 텍스트 파일 경로 (생략하면 실행 중 직접 입력)",
    )

    parser.add_argument("--model", default=model_name, help="사용할 Gemini 모델명")
    parser.add_argument(
        "--prompt-file",
        default=str(DEFAULT_PROMPT_PATH),
        help=f"시스템 프롬프트 파일 경로 (기본: {DEFAULT_PROMPT_PATH.name})",
    )
    parser.add_argument("-o", "--output", default=None, help="결과 JSON 저장 경로 (기본: 입력파일명.json)")
    args = parser.parse_args()

    print("=" * 50)
    print("Text2Schedule - Gemini 일정 추출")
    print("=" * 50)

    # simple.py와 동일하게, 파일명을 인자로 주지 않으면 실행 중 직접 입력받습니다.
    if args.input_file:
        file_name = args.input_file
    else:
        file_name = input("\n텍스트 파일명을 입력하세요: ").strip()

    input_path = Path(file_name)
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_name}")
        sys.exit(1)

    try:
        message = input_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("❌ 파일 인코딩을 읽을 수 없습니다. UTF-8 형식의 텍스트 파일을 사용해주세요.")
        sys.exit(1)

    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    
    meta_prompt = load_meta_prompt(Path(args.prompt_file))

    print(f"\n📩 입력 파일: {input_path}")
    print(f"📜 프롬프트 파일: {args.prompt_file}")

    try:
        events = extract_schedule(
            message=message,
            meta_prompt=meta_prompt,
            client=client,
            model_name=args.model,
        )
    except Exception as e:
        print(f"\n❌ 일정 추출 중 오류가 발생했습니다: {e}")
        sys.exit(1)

    print("\n[추출 결과]")
    print(json.dumps(events, ensure_ascii=False, indent=4))

    output_path = (
        Path(args.output)
        if args.output
        else input_path.with_name(f"{input_path.stem}_gemini.json")
    )
    
    save_events(events, output_path)

    print(f"\n✅ JSON 파일이 생성되었습니다: {output_path}")

    if not events:
        print("ℹ️ 일정으로 판단된 내용이 없습니다.")
    else:
        for event in events:
            if event.get("needs_review"):
                print(f"⚠️ 확인 필요: {event.get('SUMMARY')} - {event.get('review_reason')}")

if __name__ == "__main__":
    main()