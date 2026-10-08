import unittest
import json
from src.validator import format_date_to_iso, format_time_to_iso, build_full_iso_datetime, normalize_schedule_data
from src.ics_calendar import generate_ics_from_schedule, iso_to_ics_dt
from src.parser import process_text_input

class TestText2ScheduleISO(unittest.TestCase):
    """Text2Schedule 일정 변환 파이프라인 및 단위 기능 테스트 모듈"""

    def test_date_iso_conversion(self):
        """날짜 ISO 변환 단위 테스트"""
        self.assertEqual(format_date_to_iso("20260824"), "2026-08-24")
        self.assertEqual(format_date_to_iso("2026-08-24"), "2026-08-24")
        self.assertIsNone(format_date_to_iso(None))

    def test_time_iso_conversion(self):
        """시간 ISO 변환 단위 테스트"""
        self.assertEqual(format_time_to_iso("100000"), "10:00:00")
        self.assertEqual(format_time_to_iso("10:00"), "10:00:00")
        self.assertEqual(format_time_to_iso("10:00:00"), "10:00:00")

    def test_build_full_iso_datetime(self):
        """확장 ISO 일시 결합 단위 테스트"""
        iso_dt = build_full_iso_datetime("2026-08-24", "10:00:00")
        self.assertEqual(iso_dt, "2026-08-24T10:00:00+09:00")

    def test_normalize_schedule_data(self):
        """일정 데이터 정규화 및 포맷 검증 테스트"""
        raw = {
            "action": "create",
            "SUMMARY": "스마트폰 사진 클래스",
            "DATE": "20260824",
            "START_TIME": "100000",
            "END_TIME": "130000",
            "LOCATION": "청년일자리스테이션"
        }
        norm = normalize_schedule_data(raw)
        self.assertEqual(norm["summary"], "스마트폰 사진 클래스")
        self.assertEqual(norm["date"], "2026-08-24")
        self.assertEqual(norm["start_iso"], "2026-08-24T10:00:00+09:00")
        self.assertEqual(norm["end_iso"], "2026-08-24T13:00:00+09:00")

    def test_ics_generation(self):
        """.ics 캘린더 생성 기능 단위 테스트"""
        schedules = [{
            "summary": "테스트 일정",
            "start_iso": "2026-08-24T10:00:00+09:00",
            "end_iso": "2026-08-24T13:00:00+09:00",
            "location": "서울역",
            "description": "준비물 챙기기"
        }]
        ics_text = generate_ics_from_schedule(schedules)
        self.assertIn("BEGIN:VCALENDAR", ics_text)
        self.assertIn("SUMMARY:테스트 일정", ics_text)
        self.assertIn("DTSTART;TZID=Asia/Seoul:20260824T100000", ics_text)

    def test_full_pipeline_sample(self):
        """전체 파이프라인 샘플 문자 변환 통합 테스트"""
        sample_msg = """
        [Web발신]
        [프로그램 안내- 청년일자리스테이션]
        신청하신 <필승!말빨연구소> 프로그램이 월요일 진행됩니다!
        - 일정: 8월 24일(월)
        - 시간: 10:00 ~ 13:00
        - 장소: 청년일자리스테이션
        """
        schedules, ics_content = process_text_input(sample_msg)
        self.assertTrue(len(schedules) > 0)
        item = schedules[0]
        self.assertIn("start_iso", item)
        self.assertIn("08-24", item["start_iso"])

if __name__ == "__main__":
    unittest.main()
