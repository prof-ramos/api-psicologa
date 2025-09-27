#!/usr/bin/env python3
"""
Performance benchmarking script for the astrological API.
"""

import asyncio
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import httpx


class PerformanceBenchmark:
    """Comprehensive performance benchmarking tool."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=60.0)
        self.results = {}

    async def benchmark_endpoint(self, name: str, endpoint: str, method: str = "GET",
                                data: dict = None, iterations: int = 10) -> dict:
        """Benchmark a specific endpoint."""
        print(f"Benchmarking {name}...")

        durations = []
        errors = []

        for i in range(iterations):
            start_time = time.time()
            try:
                if method.upper() == "POST":
                    response = await self.client.post(endpoint, json=data)
                else:
                    response = await self.client.get(endpoint)

                duration = time.time() - start_time
                durations.append(duration)

                if response.status_code >= 400:
                    errors.append(f"HTTP {response.status_code}")

            except Exception as e:
                duration = time.time() - start_time
                durations.append(duration)
                errors.append(str(e))

            print(f"  Iteration {i+1}/{iterations}: {duration:.3f}s")

        # Calculate statistics
        if durations:
            durations.sort()
            stats = {
                "endpoint": endpoint,
                "method": method,
                "iterations": iterations,
                "total_duration": sum(durations),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "median_duration": durations[len(durations) // 2],
                "p95_duration": durations[int(len(durations) * 0.95)],
                "error_count": len(errors),
                "error_rate": len(errors) / iterations * 100,
                "requests_per_second": iterations / sum(durations) if sum(durations) > 0 else 0
            }

            if errors:
                stats["errors"] = errors[:5]  # First 5 errors

            return stats

        return {"error": "All requests failed"}

    async def cache_performance_test(self) -> dict:
        """Test cache performance with repeated identical requests."""
        print("Testing cache performance...")

        test_data = {
            "name": "Cache Test",
            "year": 1990,
            "month": 6,
            "day": 15,
            "hour": 12,
            "minute": 0,
            "city": "London",
            "nation": "GB"
        }

        # Cold request (cache miss)
        start_time = time.time()
        response1 = await self.client.post("/api/v1/astrology/subject", json=test_data)
        cold_duration = time.time() - start_time

        # Warm requests (cache hits)
        warm_durations = []
        for i in range(5):
            start_time = time.time()
            response = await self.client.post("/api/v1/astrology/subject", json=test_data)
            warm_duration = time.time() - start_time
            warm_durations.append(warm_duration)

        avg_warm_duration = sum(warm_durations) / len(warm_durations)
        cache_speedup = cold_duration / avg_warm_duration if avg_warm_duration > 0 else 0

        return {
            "cold_request_duration": cold_duration,
            "avg_warm_request_duration": avg_warm_duration,
            "cache_speedup": cache_speedup,
            "warm_requests": len(warm_durations)
        }

    async def concurrent_load_test(self, endpoint: str, concurrent_users: int = 10,
                                  requests_per_user: int = 5, method: str = "GET",
                                  data: dict = None) -> dict:
        """Test performance under concurrent load."""
        print(f"Running concurrent load test: {concurrent_users} users, {requests_per_user} requests each")

        async def user_requests():
            durations = []
            errors = []

            for _ in range(requests_per_user):
                start_time = time.time()
                try:
                    if method.upper() == "POST":
                        response = await self.client.post(endpoint, json=data)
                    else:
                        response = await self.client.get(endpoint)

                    duration = time.time() - start_time
                    durations.append(duration)

                    if response.status_code >= 400:
                        errors.append(response.status_code)

                except Exception as e:
                    duration = time.time() - start_time
                    durations.append(duration)
                    errors.append(str(e))

                await asyncio.sleep(0.1)  # Small delay between requests

            return durations, errors

        # Run concurrent users
        start_time = time.time()
        tasks = [user_requests() for _ in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        # Aggregate results
        all_durations = []
        all_errors = []

        for durations, errors in results:
            all_durations.extend(durations)
            all_errors.extend(errors)

        if all_durations:
            all_durations.sort()
            total_requests = len(all_durations)
            successful_requests = total_requests - len(all_errors)

            return {
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "error_count": len(all_errors),
                "success_rate": successful_requests / total_requests * 100,
                "total_time": total_time,
                "requests_per_second": total_requests / total_time,
                "avg_response_time": sum(all_durations) / len(all_durations),
                "median_response_time": all_durations[len(all_durations) // 2],
                "p95_response_time": all_durations[int(len(all_durations) * 0.95)],
                "p99_response_time": all_durations[int(len(all_durations) * 0.99)]
            }

        return {"error": "All requests failed"}

    async def memory_usage_test(self) -> dict:
        """Test memory usage patterns."""
        print("Testing memory usage patterns...")

        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Make many requests to test memory leaks
            test_data = {
                "name": f"Memory Test {i}",
                "year": 1990,
                "month": 6,
                "day": 15,
                "hour": 12,
                "minute": 0,
                "city": "London",
                "nation": "GB"
            }

            memory_samples = [initial_memory]

            for i in range(50):
                test_data["name"] = f"Memory Test {i}"
                await self.client.post("/api/v1/astrology/subject", json=test_data)

                if i % 10 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)

            final_memory = process.memory_info().rss / 1024 / 1024
            memory_growth = final_memory - initial_memory

            return {
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "memory_samples": memory_samples,
                "requests_tested": 50
            }

        except ImportError:
            return {"error": "psutil not available for memory testing"}

    async def run_comprehensive_benchmark(self) -> dict:
        """Run complete performance benchmark suite."""
        print("=" * 60)
        print("ASTROLOGICAL API PERFORMANCE BENCHMARK")
        print("=" * 60)
        print(f"Target URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()

        benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "tests": {}
        }

        # Test 1: Health endpoint
        benchmark_results["tests"]["health"] = await self.benchmark_endpoint(
            "Health Check",
            "/api/v1/health/",
            iterations=20
        )

        # Test 2: Astrological subject creation
        test_subject = {
            "name": "Benchmark Subject",
            "year": 1990,
            "month": 6,
            "day": 15,
            "hour": 12,
            "minute": 0,
            "city": "London",
            "nation": "GB"
        }

        benchmark_results["tests"]["subject_creation"] = await self.benchmark_endpoint(
            "Subject Creation",
            "/api/v1/astrology/subject",
            method="POST",
            data=test_subject,
            iterations=10
        )

        # Test 3: Natal chart generation
        chart_request = {
            "subject": test_subject,
            "chart_type": "natal",
            "include_aspects": True
        }

        benchmark_results["tests"]["natal_chart"] = await self.benchmark_endpoint(
            "Natal Chart Generation",
            "/api/v1/astrology/natal-chart",
            method="POST",
            data=chart_request,
            iterations=5
        )

        # Test 4: Cache performance
        benchmark_results["tests"]["cache_performance"] = await self.cache_performance_test()

        # Test 5: Concurrent load test (light)
        benchmark_results["tests"]["concurrent_load"] = await self.concurrent_load_test(
            "/api/v1/astrology/subject",
            concurrent_users=5,
            requests_per_user=3,
            method="POST",
            data=test_subject
        )

        # Test 6: Memory usage
        benchmark_results["tests"]["memory_usage"] = await self.memory_usage_test()

        return benchmark_results

    def print_summary(self, results: dict):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        for test_name, test_results in results["tests"].items():
            if "error" in test_results:
                print(f"\n{test_name.upper()}: ERROR - {test_results['error']}")
                continue

            print(f"\n{test_name.upper()}:")

            if "avg_duration" in test_results:
                print(f"  Average Duration: {test_results['avg_duration']:.3f}s")
                print(f"  Min/Max Duration: {test_results['min_duration']:.3f}s / {test_results['max_duration']:.3f}s")
                print(f"  P95 Duration: {test_results['p95_duration']:.3f}s")
                print(f"  Requests/Second: {test_results['requests_per_second']:.2f}")
                print(f"  Error Rate: {test_results['error_rate']:.1f}%")

            if "cache_speedup" in test_results:
                print(f"  Cold Request: {test_results['cold_request_duration']:.3f}s")
                print(f"  Warm Request: {test_results['avg_warm_request_duration']:.3f}s")
                print(f"  Cache Speedup: {test_results['cache_speedup']:.2f}x")

            if "success_rate" in test_results:
                print(f"  Success Rate: {test_results['success_rate']:.1f}%")
                print(f"  Concurrent Users: {test_results['concurrent_users']}")
                print(f"  Total Requests: {test_results['total_requests']}")

            if "memory_growth_mb" in test_results:
                print(f"  Initial Memory: {test_results['initial_memory_mb']:.1f} MB")
                print(f"  Final Memory: {test_results['final_memory_mb']:.1f} MB")
                print(f"  Memory Growth: {test_results['memory_growth_mb']:.1f} MB")

    async def save_results(self, results: dict, filename: str = None):
        """Save benchmark results to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        filepath = Path(filename)
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to: {filepath.absolute()}")

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


async def main():
    """Main benchmark runner."""
    parser = argparse.ArgumentParser(description="Performance benchmark for astrological API")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--quick", action="store_true", help="Run quick benchmark")

    args = parser.parse_args()

    benchmark = PerformanceBenchmark(args.url)

    try:
        if args.quick:
            print("Running quick benchmark...")
            # Quick health check
            result = await benchmark.benchmark_endpoint(
                "Quick Health Check",
                "/api/v1/health/",
                iterations=5
            )
            print(f"Health check avg: {result.get('avg_duration', 'N/A'):.3f}s")
        else:
            # Full benchmark suite
            results = await benchmark.run_comprehensive_benchmark()
            benchmark.print_summary(results)

            if args.output:
                await benchmark.save_results(results, args.output)

    except Exception as e:
        print(f"Benchmark failed: {e}")
    finally:
        await benchmark.close()


if __name__ == "__main__":
    asyncio.run(main())