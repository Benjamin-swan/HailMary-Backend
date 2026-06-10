"""AccountMapper 영속성 왕복 + 조건부 last_used 복원 단위 테스트 (DB 미접촉).

실DB 통합 테스트는 이 레포 테스트 컨벤션(전부 in-memory/fake)과 어긋나고 MySQL 의존을
들이므로, ORM↔Entity 변환의 조건부 분기만 순수 검증한다.
(server_default refresh 가드와 009 마이그레이션 정합은 로컬 alembic upgrade + 앱 부팅으로 수동 확인.)

대상:
    1. to_orm → to_entity 왕복 — 전체 필드 보존 (last_used 포함)
    2. last_used 4개 키 모두 채워짐 → 복원 O
    3. last_used 일부만 NULL(부분 조합) → 복원 None (조건부 가드)
    4. birth_time/birth_time_unknown 만 NULL → 나머지로 복원 O (가드 비포함 필드)
    5. apply_to_orm — 가변 필드 갱신, last_used None이면 기존 유지(덮어쓰기 안 함)
"""

from datetime import date, time

from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.value_object.calendar_type import CalendarType
from app.domains.auth.domain.value_object.gender import Gender
from app.domains.auth.domain.value_object.last_used_profile import LastUsedProfile
from app.domains.auth.domain.value_object.provider import Provider
from app.domains.auth.infrastructure.mapper.account_mapper import AccountMapper
from app.domains.auth.infrastructure.orm.account_orm import AccountORM


def _full_last_used() -> LastUsedProfile:
    return LastUsedProfile(
        name="홍길동",
        birth_date=date(1995, 3, 1),
        calendar_type=CalendarType.SOLAR,
        birth_time=time(11, 30),
        birth_time_unknown=False,
        gender=Gender.MALE,
    )


def test_roundtrip_preserves_fields() -> None:
    entity = Account(
        provider=Provider.KAKAO,
        provider_user_id="999",
        email="a@b.com",
        email_verified=True,
        nickname="깨비",
        profile_image_url="http://img",
        last_used=_full_last_used(),
    )
    orm = AccountMapper.to_orm(entity)
    restored = AccountMapper.to_entity(orm)

    assert restored.provider == Provider.KAKAO
    assert restored.provider_user_id == "999"
    assert restored.email == "a@b.com"
    assert restored.email_verified is True
    assert restored.nickname == "깨비"
    assert restored.profile_image_url == "http://img"
    assert restored.last_used == _full_last_used()


def test_last_used_restored_when_all_required_present() -> None:
    orm = AccountORM(
        provider=Provider.GOOGLE,
        provider_user_id="1",
        email_verified=False,
        last_name="김철수",
        last_birth_date=date(2000, 1, 1),
        last_calendar_type=CalendarType.LUNAR,
        last_birth_time=None,
        last_birth_time_unknown=True,
        last_gender=Gender.FEMALE,
    )
    entity = AccountMapper.to_entity(orm)

    assert entity.last_used is not None
    assert entity.last_used.name == "김철수"
    assert entity.last_used.birth_time is None
    assert entity.last_used.birth_time_unknown is True


def test_last_used_none_when_required_field_missing() -> None:
    # last_gender만 빠져도(부분 조합) 복원하지 않는다 — 불완전 prefill 방지
    orm = AccountORM(
        provider=Provider.KAKAO,
        provider_user_id="2",
        email_verified=False,
        last_name="홍길동",
        last_birth_date=date(1990, 5, 5),
        last_calendar_type=CalendarType.SOLAR,
        last_gender=None,
    )
    entity = AccountMapper.to_entity(orm)
    assert entity.last_used is None


def test_apply_to_orm_updates_mutable_fields() -> None:
    orm = AccountORM(
        provider=Provider.KAKAO,
        provider_user_id="3",
        email="old@b.com",
        email_verified=False,
        nickname="옛닉",
    )
    updated = Account(
        provider=Provider.KAKAO,
        provider_user_id="3",
        email="new@b.com",
        email_verified=True,
        nickname="새닉",
        last_used=_full_last_used(),
    )
    AccountMapper.apply_to_orm(updated, orm)

    assert orm.email == "new@b.com"
    assert orm.email_verified is True
    assert orm.nickname == "새닉"
    assert orm.last_name == "홍길동"  # last_used 반영됨


def test_apply_to_orm_does_not_wipe_last_used_when_none() -> None:
    # 재로그인(last_used 없는 갱신)이 기존 마지막 사용값을 지우지 않아야 한다
    orm = AccountORM(
        provider=Provider.KAKAO,
        provider_user_id="4",
        email_verified=True,
        last_name="기존이름",
        last_birth_date=date(1988, 8, 8),
        last_calendar_type=CalendarType.SOLAR,
        last_gender=Gender.MALE,
    )
    relogin = Account(
        provider=Provider.KAKAO,
        provider_user_id="4",
        email="x@y.com",
        email_verified=True,
        last_used=None,
    )
    AccountMapper.apply_to_orm(relogin, orm)

    assert orm.last_name == "기존이름"  # 보존
    assert orm.email == "x@y.com"      # 갱신
