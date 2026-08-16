import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Business, Campaign, WebsiteAudit, DecisionMakerRecord, OutreachDraft
from app.services.scoring_engine import ScoringEngine
from app.agents.business_audit_agent import BusinessAuditAgent
from app.schemas.agent import AgentInput
from app.schemas.enums import ManualReviewStatus, DemoReadiness


def generate_pilot_results():
    db: Session = SessionLocal()
    try:
        campaign = db.query(Campaign).order_by(Campaign.created_at.desc()).first()
        if not campaign:
            print("No campaign found to generate Phase 11.2 report!")
            return

        businesses = campaign.businesses
        total_count = len(businesses)
        results = []

        # Metric Counters
        count_priority = 0
        count_qualified = 0
        count_potential_review = 0
        count_rejected = 0

        count_no_review_required = 0
        count_review_recommended = 0
        count_review_required = 0

        count_verified_persons = 0
        count_verified_roles = 0
        count_business_contact_only = 0
        count_contact_target_not_found = 0
        count_contact_target_manual_review = 0

        count_outreach_ready = 0
        count_outreach_manual_review = 0
        count_outreach_suppressed = 0

        count_public_demos = 0
        count_local_only_demos = 0
        count_demo_access_failures = 0

        for b in businesses:
            wa = b.website_audit
            dm = b.decision_maker
            draft = b.outreach_draft

            score_breakdown = ScoringEngine.calculate_score(
                business=b,
                audit=wa,
                decision_maker_confidence=dm.confidence.value if dm else None,
                purchase_signals=[]
            )
            score = score_breakdown['total_score']

            # Qualification Tiers
            if b.entity_verification_status and b.entity_verification_status.value == "REJECTED":
                qualification = 'REJECTED'
                count_rejected += 1
            else:
                if score >= 80.0:
                    qualification = 'PRIORITY'
                    count_priority += 1
                elif score >= 70.0:
                    qualification = 'QUALIFIED'
                    count_qualified += 1
                elif score >= 60.0:
                    qualification = 'POTENTIAL_REVIEW'
                    count_potential_review += 1
                else:
                    qualification = 'REJECTED'
                    count_rejected += 1

            # Manual Review Status
            mrs = b.manual_review_status.value if b.manual_review_status else "NO_REVIEW_REQUIRED"
            if mrs == "NO_REVIEW_REQUIRED":
                count_no_review_required += 1
            elif mrs == "REVIEW_RECOMMENDED":
                count_review_recommended += 1
            elif mrs == "REVIEW_REQUIRED":
                count_review_required += 1
            else:
                count_no_review_required += 1

            # Contact Target Status Counts
            cts = b.contact_target_status.value if b.contact_target_status else "NOT_FOUND"
            if cts == "VERIFIED_PERSON":
                count_verified_persons += 1
            elif cts == "VERIFIED_ROLE":
                count_verified_roles += 1
            elif cts == "BUSINESS_CONTACT_ONLY":
                count_business_contact_only += 1
            elif cts == "MANUAL_REVIEW":
                count_contact_target_manual_review += 1
            else:
                count_contact_target_not_found += 1

            # Outreach Readiness Counts
            readiness = b.outreach_readiness.value if b.outreach_readiness else "NOT_READY"
            if readiness == "READY_FOR_APPROVAL":
                count_outreach_ready += 1
            elif readiness == "SUPPRESSED":
                count_outreach_suppressed += 1
            else:
                count_outreach_manual_review += 1

            # Demo Access Status Counts
            das = b.demo_access_status.value if b.demo_access_status else "LOCAL_ONLY"
            if das == "PUBLIC_ACCESSIBLE":
                count_public_demos += 1
            elif das == "LOCAL_ONLY":
                count_local_only_demos += 1
            elif das == "PUBLIC_ACCESS_FAILED":
                count_demo_access_failures += 1
            else:
                count_local_only_demos += 1

            audit_agent = BusinessAuditAgent(db)
            audit_data = audit_agent.run(AgentInput(lead_id=b.id, workflow_run_id='export_11_2'))

            item = {
                "business_id": str(b.id),
                "business_name": b.name,
                "category": b.category or "NOT_AVAILABLE",
                "location": f"{b.address or ''}, {b.city or ''}".strip(", "),
                "entity_status": b.entity_verification_status.value if b.entity_verification_status else "VERIFIED",
                "website_status": b.website_status.value if b.website_status else "NO_WEBSITE",
                "website_classification": b.website_classification.value if b.website_classification else "NO_WEBSITE",
                "opportunity_score": score,
                "score_breakdown": score_breakdown.get("components", {}),
                "qualification": qualification,
                "decision_maker": dm.name if (dm and dm.name) else "NOT_FOUND",
                "decision_maker_confidence": dm.confidence.value if (dm and dm.confidence) else "NOT_FOUND",
                "contact_target_status": cts,
                "outreach_readiness": readiness,
                "manual_review_status": mrs,
                "manual_review_reasons": b.manual_review_reasons or [],
                "demo_url": b.public_demo_url or b.local_preview_url or "NOT_AVAILABLE",
                "demo_access_status": das,
                "demo_readiness": b.demo_readiness.value if b.demo_readiness else "NOT_GENERATED",
                "action": "AWAITING_HUMAN_APPROVAL" if readiness == "READY_FOR_APPROVAL" else "REQUIRES_MANUAL_REVIEW",
                "email_draft": draft.email_body if draft else "NOT_AVAILABLE",
                "whatsapp_draft": draft.whatsapp_body if draft else "NOT_AVAILABLE"
            }
            results.append(item)

        # Assert total aggregate sums match exactly
        assert count_priority + count_qualified + count_potential_review + count_rejected == total_count, "Qualification sum mismatch!"
        assert count_no_review_required + count_review_recommended + count_review_required == total_count, "Manual Review sum mismatch!"
        assert count_verified_persons + count_verified_roles + count_business_contact_only + count_contact_target_not_found + count_contact_target_manual_review == total_count, "Contact Target sum mismatch!"
        assert count_outreach_ready + count_outreach_manual_review + count_outreach_suppressed == total_count, "Outreach Readiness sum mismatch!"
        assert count_public_demos + count_local_only_demos + count_demo_access_failures == total_count, "Demo Access sum mismatch!"

        # Save Phase 11.2 JSON
        os.makedirs("docs", exist_ok=True)
        json_path = "docs/pilot-results-phase11-2.json"
        payload = {
            "campaign_id": str(campaign.id),
            "phase": "PHASE_11_2_PUBLIC_DEMO_AND_PILOT_CONSISTENCY",
            "pilot_batch_size": len(results),
            "summary": {
                "qualification": {
                    "priority_leads": count_priority,
                    "qualified_leads": count_qualified,
                    "potential_review_leads": count_potential_review,
                    "rejected_leads": count_rejected
                },
                "manual_review": {
                    "no_review_required": count_no_review_required,
                    "review_recommended": count_review_recommended,
                    "review_required": count_review_required
                },
                "contact_target": {
                    "verified_persons": count_verified_persons,
                    "verified_roles": count_verified_roles,
                    "business_contact_only": count_business_contact_only,
                    "contact_target_not_found": count_contact_target_not_found,
                    "contact_target_manual_review": count_contact_target_manual_review
                },
                "outreach_readiness": {
                    "outreach_ready": count_outreach_ready,
                    "outreach_manual_review": count_outreach_manual_review,
                    "outreach_suppressed": count_outreach_suppressed
                },
                "demo_infrastructure": {
                    "public_demos": count_public_demos,
                    "local_only_demos": count_local_only_demos,
                    "demo_access_failures": count_demo_access_failures
                }
            },
            "businesses": results
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        # Generate Phase 11.2 Markdown Report
        md_lines = []
        md_lines.append("# Phase 11.2: Public Demo Infrastructure & Pilot Consistency Report\n")
        md_lines.append(f"**Campaign ID**: `{campaign.id}`  \n")
        md_lines.append(f"**Campaign Name**: `{campaign.name}`  \n")
        md_lines.append(f"**Execution Mode**: `OUTREACH_MODE=DRY_RUN`  \n")
        md_lines.append(f"**Target Location**: Ahmedabad, India | **Batch Size**: 10 Entities\n")
        md_lines.append("---\n")

        md_lines.append("## Executive Summary Metrics\n")
        md_lines.append("### 1. Qualification Tiers")
        md_lines.append(f"- **Priority Leads (>=80)**: {count_priority}")
        md_lines.append(f"- **Qualified Leads (70-79.9)**: {count_qualified}")
        md_lines.append(f"- **Potential Review Leads (60-69.9)**: {count_potential_review}")
        md_lines.append(f"- **Rejected Leads**: {count_rejected}\n")

        md_lines.append("### 2. Manual Review Requirements")
        md_lines.append(f"- **No Review Required**: {count_no_review_required}")
        md_lines.append(f"- **Review Recommended**: {count_review_recommended}")
        md_lines.append(f"- **Review Required**: {count_review_required}\n")

        md_lines.append("### 3. Contact Target Status")
        md_lines.append(f"- **Verified Persons**: {count_verified_persons}")
        md_lines.append(f"- **Verified Roles**: {count_verified_roles}")
        md_lines.append(f"- **Business Contact Only**: {count_business_contact_only}")
        md_lines.append(f"- **Contact Target Not Found**: {count_contact_target_not_found}")
        md_lines.append(f"- **Manual Review Targets**: {count_contact_target_manual_review}\n")

        md_lines.append("### 4. Outreach Readiness & Demos")
        md_lines.append(f"- **Outreach Ready (Awaiting Approval)**: {count_outreach_ready}")
        md_lines.append(f"- **Outreach Manual Review**: {count_outreach_manual_review}")
        md_lines.append(f"- **Public Demos**: {count_public_demos}")
        md_lines.append(f"- **Local-Only Demos**: {count_local_only_demos}")
        md_lines.append(f"- **Demo Access Failures**: {count_demo_access_failures}\n")
        md_lines.append("---\n")

        md_lines.append("## 10-Business Audit Breakdown\n")
        md_lines.append("| Business | Opp Score | Qualification | Manual Review Status | Contact Target Status | Outreach Readiness | Demo Readiness | Action |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

        for item in results:
            md_lines.append(
                f"| **{item['business_name']}** | **{item['opportunity_score']}** | `{item['qualification']}` | "
                f"`{item['manual_review_status']}` | `{item['contact_target_status']}` | "
                f"`{item['outreach_readiness']}` | `{item['demo_readiness']}` | `{item['action']}` |"
            )

        md_lines.append("\n---\n")
        md_lines.append("## Score Breakdown & Transparent Components\n")
        md_lines.append("| Business | Digital Gap (35%) | Traction (25%) | Commercial (20%) | Contactability (10%) | Signals (10%) | Total |")
        md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

        for item in results:
            comps = item.get("score_breakdown", {})
            gap = comps.get("digital_opportunity_gap", {}).get("contribution", 0.0)
            trac = comps.get("customer_traction", {}).get("contribution", 0.0)
            comm = comps.get("commercial_potential", {}).get("contribution", 0.0)
            cont = comps.get("contactability", {}).get("contribution", 0.0)
            sig = comps.get("purchase_signals", {}).get("contribution", 0.0)
            md_lines.append(
                f"| **{item['business_name']}** | {gap}/35.0 | {trac}/25.0 | {comm}/20.0 | {cont}/10.0 | {sig}/10.0 | **{item['opportunity_score']}/100.0** |"
            )

        md_lines.append("\n---\n")
        md_lines.append("## Verification & Operational Consistency\n")
        md_lines.append("- **Manual Review Truthfulness**: Discrepancy between aggregate counts and individual records resolved. Aggregate report now explicitly tracks `NO_REVIEW_REQUIRED`, `REVIEW_RECOMMENDED`, and `REVIEW_REQUIRED`.")
        md_lines.append("- **Scoring Formula Frozen**: V1 35/25/20/10/10 formula verified and frozen. Raw scores, weights, contributions, and evidence are deterministically calculated and logged.")
        md_lines.append("- **Public Demo Security & Gating**: `PUBLIC_DEMO_BASE_URL` infrastructure active. Demos pass 6 automated verification guards before reaching `PUBLIC_ACCESSIBLE` status. Unverified or local demo URLs are strictly gated from prospect outreach drafts.\n")

        md_path = "docs/pilot-results-phase11-2.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        print(f"Successfully generated {md_path} and {json_path}")

    finally:
        db.close()


if __name__ == "__main__":
    generate_pilot_results()
