from pydantic import BaseModel


class SurveyResponse(BaseModel):
    surveyId: int
