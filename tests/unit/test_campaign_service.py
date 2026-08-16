from app.schemas.campaign import CampaignCreate
from app.services.campaign_service import CampaignService


def test_create_and_get_campaign(db_session):
    camp_in = CampaignCreate(
        name="Ahmedabad Cafe Campaign",
        industry="cafe",
        city="Ahmedabad",
        min_opportunity_score=75
    )
    campaign = CampaignService.create_campaign(db_session, camp_in)
    assert campaign.id is not None
    assert campaign.name == "Ahmedabad Cafe Campaign"
    assert campaign.min_opportunity_score == 75

    fetched = CampaignService.get_campaign(db_session, campaign.id)
    assert fetched is not None
    assert fetched.id == campaign.id


def test_list_campaigns(db_session):
    camp1 = CampaignCreate(name="Camp 1", is_active=True)
    camp2 = CampaignCreate(name="Camp 2", is_active=False)
    CampaignService.create_campaign(db_session, camp1)
    CampaignService.create_campaign(db_session, camp2)

    all_camps = CampaignService.list_campaigns(db_session, active_only=False)
    assert len(all_camps) == 2

    active_camps = CampaignService.list_campaigns(db_session, active_only=True)
    assert len(active_camps) == 1
    assert active_camps[0].name == "Camp 1"
