from enum import Enum


# user 도메인 Gender와 값 동일 — 도메인 간 직접 import 금지 원칙으로 auth 자체 정의.
# (payment 도메인이 CharacterCode를 자체 정의한 것과 같은 패턴)
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
