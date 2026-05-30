"""깨비 일일사주 응답 DTO — 프론트 SajuResult JSON과 1:1 일치.

프론트가 camelCase(kkebiMood, timeFlow, displayDate)를 기대하므로 그대로 필드명 사용.
"""
from __future__ import annotations

from pydantic import BaseModel


class BirthView(BaseModel):
    date: str
    hour: int | None


class UserView(BaseModel):
    name: str
    birth: BirthView
    gender: str  # "M" | "F" | "X" (입력값 에코)


class CycleView(BaseModel):
    id: str          # YYYYMMDD
    displayDate: str  # "2026년 5월 22일"


class TotalView(BaseModel):
    score: int
    summary: str
    kkebiMood: str   # high|mid-high|mid|low


class TimeSlotView(BaseModel):
    score: int
    comment: str
    tip: str


class TimeFlowView(BaseModel):
    morning: TimeSlotView
    afternoon: TimeSlotView
    night: TimeSlotView


class BlocksView(BaseModel):
    bok: str
    gyeong: str
    jo: str


class AreaView(BaseModel):
    score: int
    summary: str
    blocks: BlocksView


class ColorView(BaseModel):
    hex: str
    name: str


class FoodView(BaseModel):
    name: str


class LuckyView(BaseModel):
    color: ColorView
    number: int
    direction: str
    food: FoodView


class DailyFortuneResponse(BaseModel):
    user: UserView
    cycle: CycleView
    total: TotalView
    timeFlow: TimeFlowView
    areas: dict[str, AreaView]  # love|work|money|health|study
    lucky: LuckyView
