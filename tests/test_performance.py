"""
Performance and load testing for the astrological API.
"""

import asyncio
import time
import pytest
import httpx
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from app.main import create_app
from app.schemas.astrology import AstrologicalSubjectRequest


class LoadTester:
    """Load testing utility for the API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    async def test_single_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Test a single request and measure performance."""
        start_time = time.time()

        try:
            if method.upper() == "POST":
                response = await self.client.post(endpoint, json=data)
            else:
                response = await self.client.get(endpoint)

            duration = time.time() - start_time

            return {
                "success": True,
                "status_code": response.status_code,
                "duration": duration,
                "response_size": len(response.content),
                "endpoint": endpoint
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "duration": duration,
                "endpoint": endpoint
            }

    async def concurrent_load_test(self, endpoint: str, concurrent_users: int, requests_per_user: int,
                                   method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Run concurrent load test."""
        async def user_session():
            """Simulate a user making multiple requests."""
            results = []
            for _ in range(requests_per_user):
                result = await self.test_single_request(endpoint, method, data)
                results.append(result)
                # Small delay between requests
                await asyncio.sleep(0.1)
            return results

        # Start concurrent user sessions
        start_time = time.time()
        tasks = [user_session() for _ in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Flatten results
        all_results = []
        for user_result in user_results:
            all_results.extend(user_result)

        # Calculate statistics
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]

        if successful_requests:
            durations = [r["duration"] for r in successful_requests]
            durations.sort()

            return {
                "total_requests": len(all_results),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": len(successful_requests) / len(all_results) * 100,
                "total_time": total_time,
                "requests_per_second": len(all_results) / total_time,
                "avg_response_time": sum(durations) / len(durations),
                "min_response_time": min(durations),
                "max_response_time": max(durations),
                "p50_response_time": durations[int(len(durations) * 0.5)],
                "p95_response_time": durations[int(len(durations) * 0.95)],
                "p99_response_time": durations[int(len(durations) * 0.99)],
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user
            }
        else:
            return {
                "total_requests": len(all_results),
                "successful_requests": 0,
                "failed_requests": len(failed_requests),
                "success_rate": 0,
                "total_time": total_time,
                "error": "All requests failed"
            }

    async def ramp_up_test(self, endpoint: str, max_users: int, ramp_duration: int,
                           method: str = "GET", data: Dict = None) -> List[Dict[str, Any]]:
        """Gradually increase load to find breaking point."""
        results = []
        user_increments = max_users // 10  # 10 steps
        step_duration = ramp_duration // 10

        for users in range(user_increments, max_users + 1, user_increments):
            print(f"Testing with {users} concurrent users...")
            result = await self.concurrent_load_test(
                endpoint, users, 5, method, data  # 5 requests per user
            )
            result["test_phase"] = f"{users}_users"
            results.append(result)

            # Break if success rate drops below 90%
            if result.get("success_rate", 0) < 90:
                print(f"Performance degraded at {users} users")
                break

            await asyncio.sleep(step_duration)

        return results

    async def stress_test(self, endpoint: str, duration_seconds: int,
                          method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """Run stress test for a specific duration."""
        results = []
        start_time = time.time()
        end_time = start_time + duration_seconds

        async def continuous_requests():
            while time.time() < end_time:
                result = await self.test_single_request(endpoint, method, data)
                results.append(result)
                await asyncio.sleep(0.01)  # Small delay

        # Run multiple concurrent request streams
        tasks = [continuous_requests() for _ in range(10)]
        await asyncio.gather(*tasks)

        # Calculate results
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        if successful_requests:
            durations = [r["duration"] for r in successful_requests]
            durations.sort()

            return {
                "test_duration": duration_seconds,
                "total_requests": len(results),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "success_rate": len(successful_requests) / len(results) * 100,
                "requests_per_second": len(results) / duration_seconds,
                "avg_response_time": sum(durations) / len(durations),
                "p95_response_time": durations[int(len(durations) * 0.95)],
            }
        else:
            return {
                "test_duration": duration_seconds,
                "total_requests": len(results),
                "error": "All requests failed"
            }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


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


@pytest.mark.asyncio
async def test_health_endpoint_performance():
    """Test health endpoint performance."""
    tester = LoadTester()

    try:
        # Single request test
        result = await tester.test_single_request("/api/v1/health/")
        assert result["success"]
        assert result["status_code"] == 200
        assert result["duration"] < 0.1  # Should be very fast

        # Concurrent test
        load_result = await tester.concurrent_load_test(
            "/api/v1/health/",
            concurrent_users=10,
            requests_per_user=5
        )

        assert load_result["success_rate"] > 95
        assert load_result["avg_response_time"] < 0.5

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_astrology_subject_performance():
    """Test astrological subject creation performance."""
    tester = LoadTester()

    try:
        # Single request test
        result = await tester.test_single_request(
            "/api/v1/astrology/subject",
            method="POST",
            data=SAMPLE_BIRTH_DATA
        )
        assert result["success"]
        assert result["status_code"] == 200
        print(f"Single request duration: {result['duration']:.3f}s")

        # Concurrent test (smaller scale due to computational intensity)
        load_result = await tester.concurrent_load_test(
            "/api/v1/astrology/subject",
            concurrent_users=3,
            requests_per_user=2,
            method="POST",
            data=SAMPLE_BIRTH_DATA
        )

        print(f"Load test results: {load_result}")
        assert load_result["success_rate"] > 80  # Allow for some computational delays

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_natal_chart_performance():
    """Test natal chart generation performance."""
    tester = LoadTester()

    try:
        # Single request test
        result = await tester.test_single_request(
            "/api/v1/astrology/natal-chart",
            method="POST",
            data=SAMPLE_CHART_REQUEST
        )
        assert result["success"]
        assert result["status_code"] == 200
        print(f"Chart generation duration: {result['duration']:.3f}s")

        # Cache effectiveness test - second request should be faster
        cached_result = await tester.test_single_request(
            "/api/v1/astrology/natal-chart",
            method="POST",
            data=SAMPLE_CHART_REQUEST
        )

        print(f"Cached request duration: {cached_result['duration']:.3f}s")
        # Cached request should be significantly faster
        assert cached_result["duration"] < result["duration"] * 0.8

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_cache_effectiveness():
    """Test that caching significantly improves performance."""
    tester = LoadTester()

    try:
        # First request (cache miss)
        start_time = time.time()
        result1 = await tester.test_single_request(
            "/api/v1/astrology/subject",
            method="POST",
            data=SAMPLE_BIRTH_DATA
        )
        first_duration = time.time() - start_time

        # Second identical request (cache hit)
        start_time = time.time()
        result2 = await tester.test_single_request(
            "/api/v1/astrology/subject",
            method="POST",
            data=SAMPLE_BIRTH_DATA
        )
        second_duration = time.time() - start_time

        assert result1["success"] and result2["success"]
        # Cache should make second request at least 50% faster
        assert second_duration < first_duration * 0.5
        print(f"Cache speedup: {first_duration / second_duration:.2f}x")

    finally:
        await tester.close()


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting works correctly."""
    tester = LoadTester()

    try:
        # Send many requests quickly to trigger rate limiting
        tasks = []
        for _ in range(70):  # More than the default 60 per minute
            task = tester.test_single_request("/api/v1/astrology/subject", "POST", SAMPLE_BIRTH_DATA)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Some requests should be rate limited (429 status)
        rate_limited = [r for r in results if r.get("status_code") == 429]
        successful = [r for r in results if r.get("status_code") == 200]

        print(f"Successful: {len(successful)}, Rate limited: {len(rate_limited)}")
        assert len(rate_limited) > 0  # Rate limiting should kick in

    finally:
        await tester.close()


if __name__ == "__main__":
    async def run_load_tests():
        """Run comprehensive load tests."""
        print("Starting load tests...")

        tester = LoadTester()

        try:
            # Test 1: Basic performance
            print("\n=== Basic Performance Test ===")
            result = await tester.test_single_request("/api/v1/health/")
            print(f"Health check: {result['duration']:.3f}s")

            # Test 2: Astrological calculation performance
            print("\n=== Astrological Calculation Test ===")
            result = await tester.test_single_request(
                "/api/v1/astrology/subject", "POST", SAMPLE_BIRTH_DATA
            )
            print(f"Subject calculation: {result['duration']:.3f}s")

            # Test 3: Concurrent load test
            print("\n=== Concurrent Load Test ===")
            load_result = await tester.concurrent_load_test(
                "/api/v1/astrology/subject",
                concurrent_users=5,
                requests_per_user=3,
                method="POST",
                data=SAMPLE_BIRTH_DATA
            )
            print(f"Success rate: {load_result['success_rate']:.1f}%")
            print(f"Avg response time: {load_result['avg_response_time']:.3f}s")
            print(f"P95 response time: {load_result['p95_response_time']:.3f}s")

            # Test 4: Cache effectiveness
            print("\n=== Cache Effectiveness Test ===")
            # First request
            result1 = await tester.test_single_request(
                "/api/v1/astrology/subject", "POST", SAMPLE_BIRTH_DATA
            )
            # Second request (should be cached)
            result2 = await tester.test_single_request(
                "/api/v1/astrology/subject", "POST", SAMPLE_BIRTH_DATA
            )
            speedup = result1["duration"] / result2["duration"]
            print(f"Cache speedup: {speedup:.2f}x")

        finally:
            await tester.close()

    # Run the tests
    asyncio.run(run_load_tests())