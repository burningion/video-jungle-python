import requests

class ApiClient:
    BASE_URL = "https://api.video-jungle.com"

    def __init__(self, token):
        self.token = token
        self.projects = Projects(self)

    def _make_request(self, method, endpoint, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

class Projects:
    def __init__(self, client):
        self.client = client

    def get(self, project_id):
        return self.client._make_request("GET", f"/projects/{project_id}")
    
    def list(self):
        return self.client._make_request("GET", "/projects")
    
    def create(self, name, description, prompt_id=None):
        if prompt_id:
            return self.client._make_request("POST", "/projects", json={"name": name, "description": description, "prompt_id": prompt_id})
        else:
            return self.client._make_request("POST", "/projects", json={"name": name, "description": description})
    
    def delete(self, project_id):
        return self.client._make_request("DELETE", f"/projects/{project_id}")