import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Business, Campaign, WebsiteAudit, DecisionMakerRecord, OutreachDraft
from app.services.scoring_engine import ScoringEngine
from app.schemas.enums import ManualReviewStatus, DemoReadiness, FinalAction
from scripts.run_phase12_validation import determine_final_action


def generate_phase12_docs():
    db: Session = SessionLocal()
    try:
        campaign = db.query(Campaign).order_by(Campaign.created_at.desc()).first()
        if not campaign:
            print("No campaign found to generate Phase 12 report!")
            return

        businesses = campaign.businesses
        total_count = len(businesses)
        results = []

        # Metric Counters
        count_valid_businesses = 0
        count_non_business = 0
        count_manual_review_entities = 0

        # Website statuses
        count_no_website = 0
        count_weak_website = 0
        count_outdated_website = 0
        count_poor_ux = 0
        count_poor_conversion = 0
        count_technically_good = 0
        count_good_website = 0
        count_excellent_website = 0
        count_conflicting_website = 0
        count_manual_review_website = 0

        # Qualification
        count_priority = 0
        count_qualified = 0
        count_potential_review = 0
        count_rejected = 0

        # Manual Review Status
        count_no_review_required = 0
        count_review_recommended = 0
        count_review_required = 0

        # Contact Target Status
        count_verified_persons = 0
        count_verified_roles = 0
        count_business_contact_only = 0
        count_contact_target_not_found = 0
        count_contact_target_manual_review = 0

        # Outreach Readiness
        count_outreach_ready = 0
        count_outreach_manual_review = 0
        count_outreach_suppressed = 0

        # Demos
        count_demos_generated = 0
        count_public_demos = 0
        count_local_only_demos = 0
        count_demo_access_failures = 0

        # Final Action Semantics
        count_action_awaiting_approval = 0
        count_action_requires_review = 0
        count_action_review_recommended = 0
        count_action_rejected = 0
        count_action_qualified_not_ready = 0

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

            # Entity classification
            evs = b.entity_verification_status.value if b.entity_verification_status else "VERIFIED"
            if evs == "REJECTED":
                count_non_business += 1
            elif evs == "MANUAL_REVIEW":
                count_manual_review_entities += 1
            else:
                count_valid_businesses += 1

            # Website classification
            wc = b.website_classification.value if b.website_classification else "NO_WEBSITE"
            if wc == "NO_WEBSITE":
                count_no_website += 1
            elif wc == "WEAK_WEBSITE":
                count_weak_website += 1
            elif wc == "OUTDATED_WEBSITE":
                count_outdated_website += 1
            elif wc == "POOR_UX":
                count_poor_ux += 1
            elif wc == "POOR_CONVERSION":
                count_poor_conversion += 1
            elif wc == "TECHNICALLY_GOOD":
                count_technically_good += 1
            elif wc == "GOOD_WEBSITE":
                count_good_website += 1
            elif wc == "EXCELLENT_WEBSITE":
                count_excellent_website += 1
            elif wc == "CONFLICTING":
                count_conflicting_website += 1
            elif wc == "MANUAL_REVIEW":
                count_manual_review_website += 1

            # Qualification Tiers
            if evs == "REJECTED":
                qualification = "REJECTED"
                count_rejected += 1
            else:
                if score >= 80.0:
                    qualification = "PRIORITY"
                    count_priority += 1
                elif score >= 70.0:
                    qualification = "QUALIFIED"
                    count_qualified += 1
                elif score >= 60.0:
                    qualification = "POTENTIAL_REVIEW"
                    count_potential_review += 1
                else:
                    qualification = "REJECTED"
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

            # Contact Target Status
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

            # Outreach Readiness
            readiness = b.outreach_readiness.value if b.outreach_readiness else "NOT_READY"
            if readiness == "READY_FOR_APPROVAL":
                count_outreach_ready += 1
            elif readiness == "SUPPRESSED":
                count_outreach_suppressed += 1
            else:
                count_outreach_manual_review += 1

            # Demo Access Status
            das = b.demo_access_status.value if b.demo_access_status else "NOT_GENERATED"
            if das != "NOT_GENERATED":
                count_demos_generated += 1
            if das == "PUBLIC_ACCESSIBLE":
                count_public_demos += 1
            elif das == "LOCAL_ONLY":
                count_local_only_demos += 1
            elif das == "PUBLIC_ACCESS_FAILED":
                count_demo_access_failures += 1

            # Final Action Semantics
            action = determine_final_action(mrs, qualification, readiness)
            if action == "AWAITING_HUMAN_OUTREACH_APPROVAL":
                count_action_awaiting_approval += 1
            elif action == "REQUIRES_MANUAL_REVIEW":
                count_action_requires_review += 1
            elif action == "REVIEW_RECOMMENDED":
                count_action_review_recommended += 1
            elif action == "REJECTED":
                count_action_rejected += 1
            elif action == "QUALIFIED_NOT_READY":
                count_action_qualified_not_ready += 1

            results.append({
                "business_id": str(b.id),
                "business_name": b.name,
                "category": b.category or "NOT_AVAILABLE",
                "location": f"{b.address or ''}, {b.city or ''}".strip(", "),
                "phone": b.phone,
                "rating": b.rating,
                "review_count": b.review_count,
                "entity_status": evs,
                "website_url": b.website_url,
                "website_status": b.website_status.value if b.website_status else "NO_WEBSITE",
                "website_classification": wc,
                "opportunity_score": score,
                "score_breakdown": score_breakdown.get("components", {}),
                "qualification": qualification,
                "decision_maker": dm.name if (dm and dm.name) else "NOT_FOUND",
                "decision_maker_title": dm.title if (dm and dm.title) else "NOT_FOUND",
                "decision_maker_confidence": dm.confidence.value if (dm and dm.confidence) else "NOT_FOUND",
                "contact_target_status": cts,
                "outreach_readiness": readiness,
                "manual_review_status": mrs,
                "manual_review_reasons": b.manual_review_reasons or [],
                "demo_url": b.public_demo_url or b.local_preview_url or "NOT_AVAILABLE",
                "demo_access_status": das,
                "action": action,
                "email_draft": draft.email_body if draft else "NOT_AVAILABLE",
                "whatsapp_draft": draft.whatsapp_body if draft else "NOT_AVAILABLE"
            })

        # Assert totals
        assert count_valid_businesses + count_non_business + count_manual_review_entities == total_count
        assert count_priority + count_qualified + count_potential_review + count_rejected == total_count
        assert count_no_review_required + count_review_recommended + count_review_required == total_count
        assert count_verified_persons + count_verified_roles + count_business_contact_only + count_contact_target_not_found + count_contact_target_manual_review == total_count
        assert count_outreach_ready + count_outreach_manual_review + count_outreach_suppressed == total_count
        assert count_action_awaiting_approval + count_action_requires_review + count_action_review_recommended + count_action_rejected + count_action_qualified_not_ready == total_count

        # Sort results by Opportunity Score descending, with Non-Business rejected at bottom
        def sort_key(item):
            # Rank: PRIORITY/QUALIFIED first, then score
            qual_rank = {"PRIORITY": 4, "QUALIFIED": 3, "POTENTIAL_REVIEW": 2, "REJECTED": 1}
            return (qual_rank.get(item["qualification"], 0), item["opportunity_score"])

        sorted_results = sorted(results, key=sort_key, reverse=True)

        # Output JSON
        os.makedirs("docs", exist_ok=True)
        json_path = "docs/pilot-results-phase12.json"
        payload = {
            "campaign_id": str(campaign.id),
            "phase": "PHASE_12_REAL_WORLD_VALIDATION",
            "batch_size": total_count,
            "entity_precision": round(count_valid_businesses / total_count, 3),
            "summary": {
                "discovery": {
                    "total_candidates": total_count,
                    "valid_businesses": count_valid_businesses,
                    "non_business_entities": count_non_business,
                    "manual_review_entities": count_manual_review_entities,
                    "entity_precision": round(count_valid_businesses / total_count, 3)
                },
                "website_verification": {
                    "no_website": count_no_website,
                    "weak_website": count_weak_website,
                    "outdated_website": count_outdated_website,
                    "poor_ux": count_poor_ux,
                    "poor_conversion": count_poor_conversion,
                    "technically_good": count_technically_good,
                    "good_website": count_good_website,
                    "excellent_website": count_excellent_website,
                    "conflicting": count_conflicting_website,
                    "manual_review": count_manual_review_website
                },
                "qualification": {
                    "priority": count_priority,
                    "qualified": count_qualified,
                    "potential_review": count_potential_review,
                    "rejected": count_rejected
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
                "demos": {
                    "demos_generated": count_demos_generated,
                    "public_demos": count_public_demos,
                    "local_only_demos": count_local_only_demos,
                    "demo_access_failures": count_demo_access_failures
                },
                "outreach": {
                    "drafts_generated": count_outreach_ready + count_outreach_manual_review,
                    "ready_for_approval": count_outreach_ready,
                    "manual_review": count_outreach_manual_review,
                    "suppressed": count_outreach_suppressed
                },
                "final_actions": {
                    "awaiting_human_outreach_approval": count_action_awaiting_approval,
                    "requires_manual_review": count_action_requires_review,
                    "review_recommended": count_action_review_recommended,
                    "rejected": count_action_rejected,
                    "qualified_not_ready": count_action_qualified_not_ready
                }
            },
            "businesses": sorted_results
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"Generated Phase 12 JSON export at {json_path}")
        return payload
    finally:
        db.close()


if __name__ == "__main__":
    generate_phase12_docs()
