from pydantic import BaseModel


class SurveyResponse(BaseModel):
    survey_id: int
    saju_request_id: int
