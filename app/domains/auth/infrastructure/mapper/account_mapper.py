from app.domains.auth.domain.entity.account import Account
from app.domains.auth.domain.value_object.last_used_profile import LastUsedProfile
from app.domains.auth.infrastructure.orm.account_orm import AccountORM


class AccountMapper:
    @staticmethod
    def to_orm(entity: Account) -> AccountORM:
        orm = AccountORM(
            id=entity.id,
            provider=entity.provider,
            provider_user_id=entity.provider_user_id,
            email=entity.email,
            email_verified=entity.email_verified,
            nickname=entity.nickname,
            profile_image_url=entity.profile_image_url,
            last_login_at=entity.last_login_at,
        )
        AccountMapper._apply_last_used(entity.last_used, orm)
        return orm

    @staticmethod
    def apply_to_orm(entity: Account, orm: AccountORM) -> None:
        """기존 row 갱신 — 가변 필드만 반영 (provider/provider_user_id는 자연키, 불변)."""
        orm.email = entity.email
        orm.email_verified = entity.email_verified
        orm.nickname = entity.nickname
        orm.profile_image_url = entity.profile_image_url
        orm.last_login_at = entity.last_login_at
        AccountMapper._apply_last_used(entity.last_used, orm)

    @staticmethod
    def _apply_last_used(last_used: LastUsedProfile | None, orm: AccountORM) -> None:
        if last_used is None:
            return  # 마지막 사용값은 덮어쓰기만 — None으로 지우지 않는다
        orm.last_name = last_used.name
        orm.last_birth_date = last_used.birth_date
        orm.last_calendar_type = last_used.calendar_type
        orm.last_birth_time = last_used.birth_time
        orm.last_birth_time_unknown = last_used.birth_time_unknown
        orm.last_gender = last_used.gender

    @staticmethod
    def to_entity(orm: AccountORM) -> Account:
        last_used: LastUsedProfile | None = None
        if (
            orm.last_name is not None
            and orm.last_birth_date is not None
            and orm.last_calendar_type is not None
            and orm.last_gender is not None
        ):
            last_used = LastUsedProfile(
                name=orm.last_name,
                birth_date=orm.last_birth_date,
                calendar_type=orm.last_calendar_type,
                birth_time=orm.last_birth_time,
                birth_time_unknown=bool(orm.last_birth_time_unknown),
                gender=orm.last_gender,
            )
        return Account(
            id=orm.id,
            provider=orm.provider,
            provider_user_id=orm.provider_user_id,
            email=orm.email,
            email_verified=orm.email_verified,
            nickname=orm.nickname,
            profile_image_url=orm.profile_image_url,
            last_used=last_used,
            created_at=orm.created_at,
            last_login_at=orm.last_login_at,
        )
