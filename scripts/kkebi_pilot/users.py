"""10명 가상 인물 — 일주 spread.

설계 원칙:
- 일간(천간 10종)을 10명에게 모두 다르게 배정 → 십성 10종이 한 번씩 다 등장
- 일지(지지 12종)는 가능한 한 분산 → 지지관계 다양성
- 성별·시진은 결과 다양성을 위한 부수 변수
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PilotUser:
    id: str
    name: str
    day_stem: str       # 일간 (천간 1자)
    day_branch: str     # 일지 (지지 1자)
    gender: str         # "F" | "M"
    birth_hour: int     # 0~23
    note: str           # 디버깅용 메모


# 일간 10천간 (양-음 교차): 甲乙丙丁戊己庚辛壬癸
# 일지 12지지에서 10개 spread: 子丑寅卯辰巳午未申酉 (戌·亥 의도적 제외해서 戊辰 일진과 더 다양한 관계)
USERS: list[PilotUser] = [
    PilotUser("u01", "수아", "甲", "子", "F", 6,  "甲子 일주 / 양간+양지"),
    PilotUser("u02", "민준", "乙", "丑", "M", 14, "乙丑 일주 / 음간+음지"),
    PilotUser("u03", "지유", "丙", "寅", "F", 9,  "丙寅 일주 / 양간+양지"),
    PilotUser("u04", "도현", "丁", "卯", "M", 22, "丁卯 일주 / 음간+음지"),
    PilotUser("u05", "서연", "戊", "辰", "F", 11, "戊辰 일주 / 양간+양지 — 오늘 일진과 동일(비견+자기)"),
    PilotUser("u06", "하준", "己", "巳", "M", 17, "己巳 일주 / 음간+음지"),
    PilotUser("u07", "지안", "庚", "午", "F", 3,  "庚午 일주 / 양간+양지"),
    PilotUser("u08", "유찬", "辛", "未", "M", 20, "辛未 일주 / 음간+음지"),
    PilotUser("u09", "예린", "壬", "申", "F", 8,  "壬申 일주 / 양간+양지"),
    PilotUser("u10", "준우", "癸", "酉", "M", 16, "癸酉 일주 / 음간+음지"),
]

# 오늘 일진 mock: 戊辰 (2026-05-28 시연용 픽스)
TODAY_STEM = "戊"
TODAY_BRANCH = "辰"
TODAY_DISPLAY = "2026년 5월 28일"
