from typing import Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.approval_service import ApprovalWorkflowService
from app.services.dispatch_engine import OutreachDispatchEngine

router = APIRouter(prefix="/approval", tags=["Approval Workflow"])


class ReviewRequest(BaseModel):
    decision: str = Field(..., description="'APPROVE' or 'REJECT'")
    reviewer: str = Field(default="Admin Reviewer")
    edits: dict[str, Any] | None = None


@router.post("/draft/{draft_id}/review", status_code=status.HTTP_200_OK)
def review_outreach_draft(draft_id: str, payload: ReviewRequest, db: Session = Depends(get_db)):
    service = ApprovalWorkflowService(db)
    try:
        res = service.review_draft(
            draft_id=draft_id,
            decision=payload.decision,
            reviewer=payload.reviewer,
            edits=payload.edits
        )
        return {"status": "success", "review": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/draft/{draft_id}/dispatch", status_code=status.HTTP_200_OK)
def dispatch_approved_outreach(draft_id: str, db: Session = Depends(get_db)):
    dispatch_engine = OutreachDispatchEngine(db)
    try:
        res = dispatch_engine.dispatch_outreach(draft_id)
        return {"status": "success", "dispatch": res}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
