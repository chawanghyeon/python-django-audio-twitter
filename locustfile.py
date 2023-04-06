# locustfile.py
from locust import HttpUser, between, task


class WebsiteTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def my_task(self):
        token_string = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgwMTE0NjkxLCJpYXQiOjE2ODAxMDc0OTEsImp0aSI6ImY5MTE5ZTJmNDZlODRkNzA5YTE5ZWFmNDY0ZTE0NWQzIiwidXNlcl9pZCI6MX0.vzv3deXvM_PV2EGRpdDTqp7ZKaYGTaFoAR0A1d_hBCQ"
        self.client.get(
            "/babble/",
            headers={"authorization": "Bearer " + token_string},
        )
