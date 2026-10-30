"""Unit tests for FastAPI REST API endpoints."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from src.api import router
from src.database import save_recording

app = FastAPI()
app.include_router(router)
client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "capabilities" in data


def test_api_recordings_and_detail():
    rec_id = save_recording(
        operation_type="transcription",
        file_name="api_test.wav",
        duration_seconds=8.0,
        sample_rate=16000,
        processing_duration_ms=400.0,
        processing_status="success",
        transcript="Testing API recordings endpoint.",
        word_count=4,
    )

    response = client.get("/api/recordings?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(r["recording_id"] == rec_id for r in data["records"])

    # Detail
    detail_resp = client.get(f"/api/recordings/{rec_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["recording_id"] == rec_id

    # 404
    not_found = client.get("/api/recordings/non_existent_id_9999")
    assert not_found.status_code == 404


def test_api_analytics_and_export():
    summary_resp = client.get("/api/analytics/summary")
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert "total_recordings" in summary

    ts_resp = client.get("/api/analytics/timeseries")
    assert ts_resp.status_code == 200
    assert "timeseries" in ts_resp.json()

    export_resp = client.get("/api/analytics/export")
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("text/csv")
    assert "recording_id" in export_resp.text


def test_api_samples():
    response = client.get("/api/samples")
    assert response.status_code == 200
    samples = response.json()
    assert len(samples) >= 2
    assert any(s["id"] == "sample_speaker_male" for s in samples)
    assert any(s["id"] == "sample_speaker_female" for s in samples)


def test_api_inspect_sample():
    response = client.post("/api/audio/inspect", data={"sample_id": "sample_speaker_male"})
    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "sample_speaker_male.wav"
    assert data["duration_seconds"] > 0
    assert "plot_url" in data

