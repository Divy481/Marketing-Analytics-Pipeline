import os
import pytest
from fastapi.testclient import TestClient

# Set sqlite DB for testing
os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"

from run_pipeline import run_pipeline
from api.main import app

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    # Run pipeline on sqlite test db before tests
    run_pipeline("sqlite:///./test_api.db")
    yield
    # Clean up test DB after test execution
    if os.path.exists("./test_api.db"):
        os.remove("./test_api.db")

def test_healthcheck():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_get_executive_summary():
    response = client.get("/api/metrics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_campaigns" in data
    assert "total_revenue" in data
    assert "overall_roas" in data
    assert data["total_campaigns"] > 0

def test_get_campaigns():
    response = client.get("/api/campaigns")
    assert response.status_code == 200
    campaigns = response.json()
    assert isinstance(campaigns, list)
    assert len(campaigns) > 0
    assert "campaign_id" in campaigns[0]

def test_get_campaigns_with_filter():
    response = client.get("/api/campaigns?channel=Meta")
    assert response.status_code == 200
    campaigns = response.json()
    assert all(c["channel"].lower() == "meta" for c in campaigns)

def test_get_campaign_by_id():
    response = client.get("/api/campaigns/C001")
    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == "C001"

def test_get_campaign_by_id_not_found():
    response = client.get("/api/campaigns/NON_EXISTENT")
    assert response.status_code == 404

def test_get_customers():
    response = client.get("/api/customers?limit=5")
    assert response.status_code == 200
    customers = response.json()
    assert len(customers) <= 5

def test_get_channel_performance():
    response = client.get("/api/channels")
    assert response.status_code == 200
    channels = response.json()
    assert isinstance(channels, list)
    assert len(channels) > 0
