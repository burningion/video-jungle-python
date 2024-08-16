import requests
from urllib import parse
from typing import List

class ApiClient:
    BASE_URL = "https://api.video-jungle.com"

    def __init__(self, token):
        self.token = token
        self.projects = Projects(self)
        self.video_files = VideoFile(self)
        self.prompts = Prompts(self)
        self.scripts = Scripts(self)
        self.assets = Assets(self)

    def _make_request(self, method, endpoint, **kwargs):
        headers = {
            "X-API-Key": self.token
        }
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

class Projects:
    def __init__(self, client):
        self.client = client

    def get(self, project_id: str):
        return self.client._make_request("GET", f"/projects/{project_id}")
    
    def list(self):
        return self.client._make_request("GET", "/projects")
    
    def create(self, name: str, description: str, prompt_id=None):
        if prompt_id:
            return self.client._make_request("POST", "/projects", json={"name": name, "description": description, "prompt_id": prompt_id})
        else:
            return self.client._make_request("POST", "/projects", json={"name": name, "description": description})
    
    def delete(self, project_id: str):
        return self.client._make_request("DELETE", f"/projects/{project_id}")
    
    def generate(self, project_id: str, script_id: str, parameters: dict):
        '''
        Generate a video using the specified project and script
        Parameters is a dictionary of the parameters required by the prompt
        '''
        parsed_parameters = parse.urlencode(parameters)
        return self.client._make_request("POST", f"/projects/{project_id}/{script_id}/generate?params={parsed_parameters}")
    
class Assets:
    def __init__(self, client):
        self.client = client
    
    def check(self, asset_id: str):
        return self.client._make_request("GET", f"/assets/check/{asset_id}")
    
    def status(self, asset_id: str):
        return self.client._make_request("GET", f"/assets/{asset_id}/status")

    def get(self, asset_id: str):
        return self.client._make_request("GET", f"/assets/{asset_id}")
    
    def list_for_project(self, project_id: str):
        return self.client._make_request("GET", f"/projects/{project_id}/asset")
    
    def list_generated_for_project(self, project_id: str):
        return self.client._make_request("GET", f"/projects/{project_id}/asset/generated")
    
    def delete(self, asset_id: str):
        return self.client._make_request("DELETE", f"/assets/{asset_id}")
    
    def download(self, asset_id: str, filename: str):
        asset = self.client._make_request("GET", f"/assets/{asset_id}")
        url = asset["download_url"]
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            return filename
        else:
            raise Exception(f"Failed to download asset: {response.text}")


    
class VideoFile:
    def __init__(self, client):
        self.client = client

    def get(self, video_file_id: str):
        return self.client._make_request("GET", f"/video-file/{video_file_id}")
    
    def list(self):
        return self.client._make_request("GET", "/video-file")
    
    def delete(self, video_file_id: str):
        return self.client._make_request("DELETE", f"/video-file/{video_file_id}")
    
    def get_analysis(self, video_file_id: str):
        return self.client._make_request("GET", f"/video-file/{video_file_id}/analysis")
    
    def create(self, name: str, filename: str, upload_method: str):
        '''
        Create a video file
        Expects an upload method of either: 'direct' or 'file-no-chunk'
        'direct' returns a signed AWS URL to upload the video file
        'file-no-chunk' expects the video file to be uploaded to Video Jungle via the
        /video-file/{video_file_id}/upload-video endpoint
        '''
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
    
    def generate(self, task: str, parameters: List[str]):
        '''
        Generates a prompt for video generation process
        Parameters is a list of the parameters required by the prompt to generate a video
        IE: ["zodiac sign", "lucky number", "lucky color"] for a horoscope reader
        '''
        return self.client._make_request("POST", "/prompts", json={"task": task, "parameters": parameters})
    
    def get(self, prompt_id: str):
        return self.client._make_request("GET", f"/prompts/{prompt_id}")
    
    def delete(self, prompt_id: str):
        return self.client._make_request("DELETE", f"/prompts/{prompt_id}")
    
class Scripts:
    def __init__(self, client):
        self.client = client
    
    def list(self, project_id: str):
        return self.client._make_request("GET", f"/projects/{project_id}/scripts")
    
    def get(self, project_id: str, script_id: str):
        return self.client._make_request("GET", f"/scripts/{project_id}/{script_id}")
    
    def create(self, project_id: str, name: str, data: dict, inputs: dict):
        return self.client._make_request("POST", f"/scripts/{project_id}/scripts", json={"name": name, "data": data, "inputs": inputs})
    
    def delete(self, project_id: str, script_id: str):
        return self.client._make_request("DELETE", f"/scripts/{project_id}/{script_id}")