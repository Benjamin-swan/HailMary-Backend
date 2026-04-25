from app.domains.user.domain.entity.user import User


class SajuDataExtractor:
    """User 엔티티를 FortuneTeller Lambda 요청 형식으로 변환한다."""

    def extract(self, user: User) -> dict:  # type: ignore[type-arg]
        birth_time = user.birth_info.birth_time_str()
        return {
            "birth": user.birth_info.birth_date.strftime("%Y-%m-%d"),
            "time": birth_time if birth_time is not None else "unknown",
            "calendar": user.birth_info.calendar_type.value,
            "gender": user.gender.value,
        }
