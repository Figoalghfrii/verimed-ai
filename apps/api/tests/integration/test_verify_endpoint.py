"""Integration tests for POST /api/v1/verify endpoint."""

from httpx import AsyncClient


async def test_verify_supported_claim_returns_grounded_demo_result(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Mencuci tangan pakai sabun dan air mengalir membantu mencegah infeksi diare.",
            "language": "id",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["meta"]["is_demonstration"] is True

    data = body["data"]
    assert data["status"] == "COMPLETED"
    assert data["is_demonstration"] is True
    assert data["persisted"] is True
    assert data["emergency_triggered"] is False
    assert "bukan alat diagnosis medis" in data["disclaimer"]

    claim = data["claims"][0]
    assert claim["assessment_id"] is not None
    assert claim["verdict"] == "SUPPORTED"
    assert claim["verdict_label_id"] == "Didukung Bukti"
    assert claim["abstained"] is False
    assert claim["citations_valid"] is True
    assert len(claim["sources"]) >= 1
    assert all(src["is_synthetic_demo"] is True for src in claim["sources"])


async def test_verify_contradicted_and_mixed_claims(async_client: AsyncClient) -> None:
    resp_contra = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Minum rebusan daun sirsak menyembuhkan semua kanker tanpa kemoterapi.",
            "language": "id",
        },
    )
    assert resp_contra.status_code == 200
    assert resp_contra.json()["data"]["claims"][0]["verdict"] == "CONTRADICTED"

    resp_mixed = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Konsumsi suplemen vitamin C dosis tinggi selalu mencegah pilek biasa.",
            "language": "id",
        },
    )
    assert resp_mixed.status_code == 200
    assert resp_mixed.json()["data"]["claims"][0]["verdict"] == "MIXED_EVIDENCE"


async def test_verify_emergency_input_triggers_emergency_halt(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Tolong, saya mengalami nyeri dada hebat dan sesak napas mendadak.",
            "language": "id",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "EMERGENCY_HALT"
    assert data["emergency_triggered"] is True
    assert data["claims"] == []
    assert data["emergency_guidance"] is not None
    assert any("119" in contact for contact in data["emergency_guidance"]["emergency_contacts"])


async def test_verify_short_input_returns_validation_error_envelope(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        "/api/v1/verify",
        json={"text": "pendek", "language": "id"},
    )
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


async def test_verify_jamu_and_ggl_demo_claims_return_calibrated_verdicts(
    async_client: AsyncClient,
) -> None:
    resp_jamu = await async_client.post(
        "/api/v1/verify",
        json={
            "text": (
                "Obat tradisional atau jamu tertentu dapat menyembuhkan penyakit kanker "
                "tanpa perlu operasi maupun terapi medis."
            ),
            "language": "id",
        },
    )
    assert resp_jamu.status_code == 200
    assert resp_jamu.json()["data"]["claims"][0]["verdict"] == "CONTRADICTED"

    resp_ggl = await async_client.post(
        "/api/v1/verify",
        json={
            "text": (
                "Membatasi asupan gula, garam, dan lemak harian membantu menurunkan risiko "
                "diabetes dan hipertensi."
            ),
            "language": "id",
        },
    )
    assert resp_ggl.status_code == 200
    assert resp_ggl.json()["data"]["claims"][0]["verdict"] == "SUPPORTED"


async def test_verify_english_claim_and_english_emergency_guidance(
    async_client: AsyncClient,
) -> None:
    resp_en = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "Washing hands regularly with soap reduces the risk of infections.",
            "language": "en",
        },
    )
    assert resp_en.status_code == 200
    data_en = resp_en.json()["data"]
    assert data_en["language"] == "en"
    assert "not a medical diagnosis tool" in data_en["disclaimer"]
    assert data_en["claims"][0]["verdict"] == "SUPPORTED"
    assert "Based on retrieved" in data_en["claims"][0]["explanation"]

    resp_em = await async_client.post(
        "/api/v1/verify",
        json={
            "text": "I have severe difficulty breathing and feel like a heart attack.",
            "language": "en",
        },
    )
    assert resp_em.status_code == 200
    data_em = resp_em.json()["data"]
    assert data_em["emergency_triggered"] is True
    assert "Potential Acute Medical Emergency" in data_em["emergency_guidance"]["headline"]
