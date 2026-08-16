from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.orchestrator.pipeline import CampaignPipelineRunner

router = APIRouter(prefix="/pipeline", tags=["Pipeline Orchestrator"])


class PipelineRunRequest(BaseModel):
    query: str = "restaurants in Ahmedabad"


@router.post("/run-campaign/{campaign_id}", status_code=status.HTTP_200_OK)
def run_campaign_pipeline(campaign_id: str, req: PipelineRunRequest = PipelineRunRequest(), db: Session = Depends(get_db)):
    runner = CampaignPipelineRunner(db)
    try:
        res = runner.run_pipeline_for_campaign(campaign_id=campaign_id, query=req.query)
        return {"status": "success", "pipeline_result": res}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
