"""_parse_pay_date 회귀 테스트 (HM-BE-81).

PayApp pay_date 는 KST 벽시계 문자열. 과거 구현이 KST 값을 UTC 라벨로 그대로 저장해
approved_at 이 9시간 미래가 됐고, 이메일 폴백 스위퍼가 9시간 지연됐다 (CS #1, 116073157).
"""

from datetime import UTC, datetime

from app.domains.payment.application.usecase.handle_payapp_feedback_usecase import (
    _parse_pay_date,
)


class TestParsePayDate:
    def test_kst_wall_clock_converts_to_utc(self) -> None:
        # CS #1 실데이터: KST 2026-06-08 01:28:56 → UTC 2026-06-07 16:28:56
        parsed = _parse_pay_date("2026-06-08 01:28:56")
        assert parsed == datetime(2026, 6, 7, 16, 28, 56, tzinfo=UTC)

    def test_result_is_utc_tzinfo(self) -> None:
        parsed = _parse_pay_date("2026-06-08 01:28:56")
        assert parsed is not None
        assert parsed.utcoffset() is not None
        assert parsed.utcoffset().total_seconds() == 0  # type: ignore[union-attr]

    def test_not_in_future_regression(self) -> None:
        # 회귀 가드: "지금" 시각의 KST 문자열을 파싱하면 절대 미래가 아니어야 한다.
        # (구버전 버그는 항상 now+9h 를 반환 → 이 테스트가 실패했음)
        from datetime import timedelta, timezone

        kst_now_str = datetime.now(timezone(timedelta(hours=9))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        parsed = _parse_pay_date(kst_now_str)
        assert parsed is not None
        assert parsed <= datetime.now(UTC) + timedelta(seconds=5)

    def test_invalid_string_returns_none(self) -> None:
        assert _parse_pay_date("not-a-date") is None
        assert _parse_pay_date("") is None
        assert _parse_pay_date(None) is None
        assert _parse_pay_date(12345) is None
