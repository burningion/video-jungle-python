import requests
from urllib import parse

class ApiClient:
    BASE_URL = "https://api.video-jungle.com"

    def __init__(self, token):
        self.token = token
        self.projects = Projects(self)
        self.video_files = VideoFile(self)
        self.prompts = Prompts(self)
        self.scripts = Scripts(self)

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
    
    def generate(self, project_id, script_id, parameters):
        parsed_parameters = parse.urlencode(parameters)
        return self.client._make_request("POST", f"/projects/{project_id}/{script_id}/generate?parameters={parsed_parameters}")
    
class VideoFile:
    def __init__(self, client):
        self.client = client

    def get(self, video_file_id):
        return self.client._make_request("GET", f"/video-file/{video_file_id}")
    
    def list(self):
        return self.client._make_request("GET", "/video-file")
    
    def delete(self, video_file_id):
        return self.client._make_request("DELETE", f"/video-file/{video_file_id}")
    
    def get_analysis(self, video_file_id):
        return self.client._make_request("GET", f"/video-file/{video_file_id}/analysis")
    
    def create(self, name, filename, upload_method):
        return self.client._make_request("POST", "/video-file", json={"name": name, "filename": filename, "upload_method": upload_method})
    
    def upload_direct(self, video_file_id, file):
        return self.client._make_request("POST", f"/video-file/{video_file_id}/upload-video", files={"file": file})
    
    def create_analysis(self, video_file_id):
        return self.client._make_request("POST", f"/video-file/{video_file_id}/analysis")

class Prompts:
    def __init__(self, client):
        self.client = client
    
    def list(self):
        return self.client._make_request("GET", "/prompts")
    
    def generate(self, task, parameters):
        return self.client._make_request("POST", "/prompts", json={"task": task, "parameters": parameters})
    
    def get(self, prompt_id):
        return self.client._make_request("GET", f"/prompts/{prompt_id}")
    
    def delete(self, prompt_id):
        return self.client._make_request("DELETE", f"/prompts/{prompt_id}")
    
class Scripts:
    def __init__(self, client):
        self.client = client
    
    def list(self, project_id):
        return self.client._make_request("GET", f"/projects/{project_id}/scripts")
    
    def get(self, project_id, script_id):
        return self.client._make_request("GET", f"/scripts/{project_id}/{script_id}")
    
    def create(self, project_id, name, data, inputs):
        return self.client._make_request("POST", f"/scripts/{project_id}/scripts", json={"name": name, "data": data, "inputs": inputs})
    
    def delete(self, project_id, script_id):
        return self.client._make_request("DELETE", f"/scripts/{project_id}/{script_id}")