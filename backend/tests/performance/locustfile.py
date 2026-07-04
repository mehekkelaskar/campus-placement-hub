from locust import HttpUser, task, between


class PlacementPortalUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def view_companies(self):
        with self.client.get(
            "/api/companies/",
            name="/api/companies/",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Expected 200, received {response.status_code}"
                )

    @task(3)
    def view_placement_drives(self):
        with self.client.get(
            "/api/companies/drives/",
            name="/api/companies/drives/",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Expected 200, received {response.status_code}"
                )

    @task(2)
    def view_company_details(self):
        with self.client.get(
            "/api/companies/1/",
            name="/api/companies/[id]/",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Expected 200, received {response.status_code}"
                )