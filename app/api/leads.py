from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.lead import BusinessCreate, BusinessResponse
from app.schemas.enums import WorkflowState
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Leads"])


@router.post("", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
def create_lead(lead_in: BusinessCreate, campaign_id: str | None = None, db: Session = Depends(get_db)):
    lead, is_new = LeadService.create_lead(db, lead_in, campaign_id=campaign_id)
    return lead


@router.get("", response_model=list[BusinessResponse])
def list_leads(
    city: str | None = None,
    category: str | None = None,
    state: WorkflowState | None = None,
    min_score: float | None = None,
    exclude_suppressed: bool = True,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return LeadService.list_leads(
        db=db,
        city=city,
        category=category,
        workflow_state=state,
        min_score=min_score,
        exclude_suppressed=exclude_suppressed,
        limit=limit,
        offset=offset
    )


@router.get("/{lead_id}", response_model=BusinessResponse)
def get_lead(lead_id: str, db: Session = Depends(get_db)):
    lead = LeadService.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.post("/{lead_id}/suppress", response_model=BusinessResponse)
def suppress_lead(lead_id: str, reason: str = "DO_NOT_CONTACT", db: Session = Depends(get_db)):
    lead = LeadService.suppress_lead(db, lead_id, reason=reason)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
