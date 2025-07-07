from fastapi import APIRouter, HTTPException
from typing import List
from models.survey import SurveyData
from db import queries

router = APIRouter()

@router.post("/survey")
async def submit_survey(survey_data: SurveyData):
    try:
        combined_experience = survey_data.ceFiExperience + survey_data.deFiExperience
        await queries.update_user_risk_profile(survey_data.xrpl_wallet_address, survey_data.riskPreference, combined_experience)
        return {"message": "Survey data submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
