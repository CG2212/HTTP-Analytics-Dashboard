from locust import HttpUser, task, between

class ProxyStressUser(HttpUser):
    # Fire requests as fast as possible
    wait_time = between(0.001, 0.005)

    @task(5)
    def test_proxy_get(self):
        # Fail the request if response time exceeds 1.5 seconds (1500ms)
        with self.client.get("/proxy/get", timeout=1.5, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.5:
                response.failure(f"Request timed out! Took {response.elapsed.total_seconds()}s")

    @task(1)
    def test_dashboard_api(self):
        with self.client.get("/api/dashboard-data", timeout=1.5, catch_response=True) as response:
            if response.elapsed.total_seconds() > 1.5:
                response.failure(f"Dashboard query timed out! Took {response.elapsed.total_seconds()}s")