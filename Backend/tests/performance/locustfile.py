"""
Locust load testing scenarios
Location: Backend/tests/performance/locustfile.py

Usage:
    # Start Locust web interface
    locust -f tests/performance/locustfile.py --host=http://localhost:8000

    # Run headless load test
    locust -f tests/performance/locustfile.py --host=http://localhost:8000 \\
           --users 100 --spawn-rate 10 --run-time 5m --headless

Test Scenarios:
- P-03: Load test - 100 concurrent user logins
- P-04: Load test - concurrent resume uploads
- P-08: API throughput - sustained request rate
"""
from locust import HttpUser, task, between, events
import random


class ResumeifyUser(HttpUser):
    """Simulated user for load testing Resumify API"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    token = None

    def on_start(self):
        """Called when a simulated user starts - login and get auth token"""
        self.login()

    def login(self):
        """Login and store authentication token"""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "test_candidate",
            "password": "TestPass123!"
        })

        if response.status_code == 200:
            try:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            except:
                self.headers = {}
        else:
            self.headers = {}

    @task(5)
    def health_check(self):
        """Test P-08: High-frequency health check endpoint"""
        self.client.get("/api/v1/health")

    @task(3)
    def search_candidates(self):
        """Test P-02: Candidate search endpoint"""
        skills = ["Python", "JavaScript", "Java", "React", "Docker"]
        skill = random.choice(skills)

        self.client.get(
            f"/api/v1/candidates/search?skills={skill}",
            headers=self.headers,
            name="/api/v1/candidates/search"
        )

    @task(2)
    def view_jobs(self):
        """Load test for job listings with pagination"""
        page = random.randint(1, 5)
        self.client.get(
            f"/api/v1/jobs/?page={page}&limit=20",
            headers=self.headers,
            name="/api/v1/jobs/"
        )

    @task(1)
    def view_profile(self):
        """Load test for profile endpoint"""
        self.client.get("/api/v1/profile/me", headers=self.headers)

    @task(1)
    def login_task(self):
        """Test P-03: Concurrent user logins"""
        self.client.post("/api/v1/auth/login", data={
            "username": "test_candidate",
            "password": "TestPass123!"
        })


class HeavyUser(HttpUser):
    """Simulated user performing heavy operations"""

    wait_time = between(2, 5)

    def on_start(self):
        """Login"""
        response = self.client.post("/api/v1/auth/login", data={
            "username": "test_candidate",
            "password": "TestPass123!"
        })

        if response.status_code == 200:
            try:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            except:
                self.headers = {}
        else:
            self.headers = {}

    @task(1)
    def upload_resume(self):
        """Test P-04: Concurrent resume uploads"""
        # Create mock PDF content
        pdf_content = b"%PDF-1.4\nMock resume content for load testing"

        files = {
            "file": ("test_resume.pdf", pdf_content, "application/pdf")
        }

        self.client.post(
            "/api/v1/upload/resume",
            files=files,
            headers=self.headers,
            name="/api/v1/upload/resume"
        )


# Event listeners for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("Load test starting...")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\nLoad test completed!")
    print(f"Total requests: {environment.stats.total.num_requests}")
    print(f"Total failures: {environment.stats.total.num_failures}")
    print(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    print(f"RPS: {environment.stats.total.total_rps:.2f}")
