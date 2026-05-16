"""
Run: locust -f locustfile.py --host=http://localhost:8000
"""

import random
import uuid

from locust import HttpUser, between, task


class DeviceUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        suffix = uuid.uuid4().hex[:8]

        r = self.client.post("/users", json={"name": f"u_{suffix}"})
        r.raise_for_status()
        self.user_id = r.json()["id"]

        r = self.client.post(
            "/devices",
            json={"name": f"d_{suffix}", "user_id": self.user_id},
        )
        r.raise_for_status()
        self.device_id = r.json()["id"]

    @task(20)
    def post_statistic(self):
        self.client.post(
            f"/devices/{self.device_id}/statistics",
            json={
                "x": random.uniform(-100, 100),
                "y": random.uniform(-100, 100),
                "z": random.uniform(-100, 100),
            },
            name="/devices/{id}/statistics",
        )

    @task(2)
    def request_device_analytics(self):
        with self.client.post(
            f"/devices/{self.device_id}/analytics",
            name="/devices/{id}/analytics",
            catch_response=True,
        ) as resp:
            if resp.status_code != 202:
                resp.failure(f"expected 202, got {resp.status_code}")

    @task(1)
    def request_user_analytics(self):
        with self.client.post(
            f"/users/{self.user_id}/analytics",
            name="/users/{id}/analytics",
            catch_response=True,
        ) as resp:
            if resp.status_code != 202:
                resp.failure(f"expected 202, got {resp.status_code}")
