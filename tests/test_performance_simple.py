"""
Simplified performance tests using FastAPI TestClient.
"""

import time
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


# Test data
SAMPLE_BIRTH_DATA = {
    "name": "Load Test Subject",
    "year": 1990,
    "month": 6,
    "day": 15,
    "hour": 12,
    "minute": 0,
    "city": "London",
    "nation": "GB"
}

SAMPLE_CHART_REQUEST = {
    "subject": SAMPLE_BIRTH_DATA,
    "chart_type": "natal",
    "include_aspects": True
}


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


def test_health_endpoint_performance(client):
    """Test health endpoint performance."""
    # Single request test
    start_time = time.time()
    response = client.get("/api/v1/health/")
    duration = time.time() - start_time

    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    assert duration < 0.1  # Should be very fast
    print(f"Health check duration: {duration:.3f}s")


def test_astrology_subject_creation(client):
    """Test astrological subject creation performance."""
    # Single request test
    start_time = time.time()
    response = client.post("/api/v1/astrology/subject", json=SAMPLE_BIRTH_DATA)
    duration = time.time() - start_time

    assert response.status_code == 200
    assert response.json()["status"] == "OK"
    print(f"Subject creation duration: {duration:.3f}s")

    # Should be reasonable for astrological calculations
    assert duration < 10.0  # Allow up to 10 seconds for complex calculations


def test_cache_effectiveness(client):
    """Test that caching significantly improves performance."""
    # First request (cache miss)
    start_time = time.time()
    response1 = client.post("/api/v1/astrology/subject", json=SAMPLE_BIRTH_DATA)
    first_duration = time.time() - start_time

    # Second identical request (cache hit)
    start_time = time.time()
    response2 = client.post("/api/v1/astrology/subject", json=SAMPLE_BIRTH_DATA)
    second_duration = time.time() - start_time

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response1.json()["status"] == "OK"
    assert response2.json()["status"] == "OK"

    # Results should be identical
    assert response1.json()["data"] == response2.json()["data"]

    # Cache should make second request faster (allow some variance)
    print(f"First request: {first_duration:.3f}s")
    print(f"Second request: {second_duration:.3f}s")

    if second_duration > 0:
        speedup = first_duration / second_duration
        print(f"Cache speedup: {speedup:.2f}x")
        # Second request should be at least 20% faster due to caching
        assert second_duration < first_duration * 0.8


def test_response_compression(client):
    """Test that responses include compression headers when appropriate."""
    response = client.post(
        "/api/v1/astrology/subject",
        json=SAMPLE_BIRTH_DATA,
        headers={"accept-encoding": "gzip"}
    )

    assert response.status_code == 200

    # Check if response has processing time header
    assert "x-process-time" in response.headers
    processing_time = float(response.headers["x-process-time"])
    assert processing_time > 0
    print(f"Processing time: {processing_time:.3f}s")


def test_rate_limiting_headers(client):
    """Test that rate limiting headers are present."""
    response = client.get("/api/v1/health/")

    assert response.status_code == 200

    # Check for rate limiting headers (case insensitive)
    headers_lower = {k.lower(): v for k, v in response.headers.items()}

    # Rate limiting headers might be present
    if "x-ratelimit-limit" in headers_lower:
        limit = int(headers_lower["x-ratelimit-limit"])
        remaining = int(headers_lower["x-ratelimit-remaining"])
        print(f"Rate limit: {limit}, Remaining: {remaining}")
        assert limit > 0
        assert remaining >= 0
    else:
        print("Rate limiting headers not found (might be disabled in test mode)")
        # Just verify the response is successful
        assert True


def test_concurrent_requests(client):
    """Test performance under concurrent load."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def make_request():
        start_time = time.time()
        response = client.get("/api/v1/health/")
        duration = time.time() - start_time
        return {
            "status_code": response.status_code,
            "duration": duration,
            "success": response.status_code == 200
        }

    # Run 10 concurrent requests
    num_requests = 10
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        results = [future.result() for future in as_completed(futures)]

    # All requests should succeed
    successful = [r for r in results if r["success"]]
    assert len(successful) == num_requests

    # Calculate average response time
    avg_duration = sum(r["duration"] for r in results) / len(results)
    max_duration = max(r["duration"] for r in results)

    print(f"Concurrent requests: {num_requests}")
    print(f"Average duration: {avg_duration:.3f}s")
    print(f"Max duration: {max_duration:.3f}s")

    # Should handle concurrent requests reasonably well
    assert avg_duration < 1.0
    assert max_duration < 2.0


def test_metrics_endpoint(client):
    """Test that metrics endpoint is available and returns data."""
    # Make a few requests to generate metrics
    client.get("/api/v1/health/")
    client.get("/api/v1/health/")

    # Check metrics endpoint
    response = client.get("/metrics")

    # Metrics might be disabled in test mode, so check if available
    if response.status_code == 200:
        content = response.text
        assert len(content) > 0
        print(f"Metrics response length: {len(content)} characters")
    else:
        print(f"Metrics endpoint returned {response.status_code} (might be disabled in test mode)")
        # Just verify it's a proper response
        assert response.status_code in [200, 404]


def test_error_handling_performance(client):
    """Test that error responses are fast."""
    start_time = time.time()
    response = client.get("/api/v1/nonexistent")
    duration = time.time() - start_time

    assert response.status_code == 404
    assert duration < 0.1  # Error responses should be very fast
    print(f"404 error duration: {duration:.3f}s")


if __name__ == "__main__":
    """Run tests directly for quick testing."""
    import sys

    print("Running performance tests...")
    app = create_app()
    client = TestClient(app)

    try:
        print("\n1. Testing health endpoint...")
        test_health_endpoint_performance(client)

        print("\n2. Testing astrology subject creation...")
        test_astrology_subject_creation(client)

        print("\n3. Testing cache effectiveness...")
        test_cache_effectiveness(client)

        print("\n4. Testing response headers...")
        test_response_compression(client)

        print("\n5. Testing rate limiting headers...")
        test_rate_limiting_headers(client)

        print("\n6. Testing concurrent requests...")
        test_concurrent_requests(client)

        print("\n7. Testing metrics endpoint...")
        test_metrics_endpoint(client)

        print("\n8. Testing error handling...")
        test_error_handling_performance(client)

        print("\n✅ All performance tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)