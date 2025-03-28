import requests
from urllib import parse
from typing import List, Optional, Set
from .model import VideoFile, Script, Prompt, Project, Asset, User, VideoSearch, VideoFilters, DurationFilter
import time
from datetime import datetime
from uuid import UUID
import httpx

class ApiClient:
    BASE_URL = "https://api.video-jungle.com"

    def __init__(self, token):
        self.token = token
        self.projects = ProjectsAPI(self)
        self.video_files = VideoFileAPI(self)
        self.prompts = PromptsAPI(self)
        self.scripts = ScriptsAPI(self)
        self.assets = AssetsAPI(self)
        self.user_account = UserAPI(self)

    def _make_request(self, method, endpoint, **kwargs):
        headers = {
            "X-API-Key": self.token
        }
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
class ProjectsAPI:
    def __init__(self, client):
        self.client = client

    def get(self, project_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}")
        return Project(**obj)
    
    def list(self):
        obj = self.client._make_request("GET", "/projects")
        return [Project(**project) for project in obj]
    
    def create(self, name: str, description: str, prompt_id=None, generation_method: str = "prompt-to-video"):
        if prompt_id:
            project = self.client._make_request("POST", "/projects", json={"name": name, "description": description, "prompt_id": prompt_id, "data": generation_method})
            return self.get(project["id"])
        else:
            project = self.client._make_request("POST", "/projects", json={"name": name, "description": description, "data": generation_method})
            return self.get(project["id"])
    
    def delete(self, project_id: str):
        return self.client._make_request("DELETE", f"/projects/{project_id}")
    
    def generate(self, project_id: str, script_id: str, parameters: dict):
        '''
        Generate a video using the specified project and script
        Parameters is a dictionary of the parameters required by the prompt
        '''
        parsed_parameters = parse.urlencode(parameters)
        return self.client._make_request("POST", f"/projects/{project_id}/{script_id}/generate?{parsed_parameters}")
    
    def render_edit(self, project_id: str, create_edit: dict):
        '''
        Render a video using the specified project and script
        Parameters is a dictionary of the parameters required by the prompt
        Returns: {"asset_id": "ffff-ffff-ffff-ffff", "asset_key": "asset-key", "edit_id": "4444-4444-4444-4444"}
        '''
        return self.client._make_request("POST", f"/projects/{project_id}/create-edit", json=create_edit)
    
    def update_edit(self, project_id: str, edit_id: str, edit: dict):
        '''
        Update an existing edit within a project
        Returns the updated edit
        '''
        return self.client._make_request("PUT", f"/projects/{project_id}/edits/{edit_id}", json=edit)
    
    def create_edit(self, project_id: str, create_edit: dict):
        '''
        Create a new edit within a project for editing before rendering
        Returns same as above
        '''
        return self.client._make_request("POST", f"/projects/{project_id}/create-edit", json=create_edit)

class AssetsAPI:
    def __init__(self, client):
        self.client = client
    
    def check(self, asset_id: str):
        return self.client._make_request("GET", f"/assets/check/{asset_id}")
    
    def status(self, asset_id: str):
        return self.client._make_request("GET", f"/assets/{asset_id}/status")

    def get(self, asset_id: str):
        obj = self.client._make_request("GET", f"/assets/{asset_id}")
        return Asset(**obj)
    
    def list_for_project(self, project_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}/asset")
        return [Asset(**asset) for asset in obj]

    def list_generated_for_project(self, project_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}/asset/generated")
        return [Asset(**asset) for asset in obj]
    
    def delete(self, asset_id: str):
        return self.client._make_request("DELETE", f"/assets/{asset_id}")
    
    def download(self, asset_id: str, filename: str, print_progress: bool = False):
        while True:
            asset = self.client._make_request("GET", f"/assets/{asset_id}")
            if asset["uploaded"]:
                break
            time.sleep(.5)
            if print_progress:
                print("Waiting for asset to be ready...")
        url = asset["download_url"]
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            return filename
        else:
            raise Exception(f"Failed to download asset: {response.text}")
    
class VideoFileAPI:
    def __init__(self, client):
        self.client = client

    def get(self, video_file_id: str):
        obj = self.client._make_request("GET", f"/video-file/{video_file_id}")
        return VideoFile(**obj)
    
    def list(self):
        obj = self.client._make_request("GET", "/video-file")
        return [VideoFile(**video_file) for video_file in obj]
    
    def delete(self, video_file_id: str):
        return self.client._make_request("DELETE", f"/video-file/{video_file_id}")
    
    def search(
        self,
        query: Optional[str] = None,
        limit: int = 10,
        project_id: Optional[str] = None,
        duration_min: Optional[float] = None,
        duration_max: Optional[float] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        tags: Optional[List[str]] = None,
        min_relevance: Optional[float] = None,
        include_segments: bool = True,
        include_related: bool = False,
        query_audio: Optional[str] = None,
        query_img: Optional[str] = None,
    ):
        """
        Search for videos with advanced filtering options.
        
        Args:
            query: Text search query
            limit: Maximum number of results to return
            project_id: Optional project ID to scope the search
            duration_min: Minimum video duration in seconds
            duration_max: Maximum video duration in seconds
            created_after: Filter videos created after this datetime
            created_before: Filter videos created before this datetime
            tags: Set of tags to filter by
            min_relevance: Minimum relevance score threshold
            include_segments: Whether to include video segments in results
            include_related: Whether to include related videos
            query_audio: Optional audio search query
            query_img: Optional image search query
        """
        # Build the filters object if any filters are specified                
        # Create the search object
    
        vs = VideoSearch.create(
            query=query,
            limit=limit,
            project_id=project_id,
            tags=tags,
            duration_min=duration_min,
            duration_max=duration_max,
            created_after=created_after,
            created_before=created_before,
            min_relevance=min_relevance,
            include_segments=include_segments,
            include_related=include_related,
            query_audio=query_audio,
            query_img=query_img
        )
        # Make the request
        return self.client._make_request("POST", "/video-file/search", json=vs.model_dump())
    
    def download(self, video_id: str, filename: str):
        video = self.get(video_id)
        url = video.download_url
        if not url:
            raise Exception("Video file has no download URL")
        with httpx.Client() as client:
                # Stream the response
                with client.stream('GET', url) as response:
                    response.raise_for_status()
                    # Open file in binary write mode
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)    
        return True

    def get_analysis(self, video_file_id: str):
        return self.client._make_request("GET", f"/video-file/{video_file_id}/analysis")
    
    def create(self, name: str, filename: str, upload_method: str = "file-no-chunk"):
        '''
        Create a video file
        Expects an upload method of either: 'url', 'direct', or 'file-no-chunk'
        'url' downloads the video file from a URL
        'direct' returns a signed AWS URL to upload the video file
        'file-no-chunk' expects the video file to be uploaded to Video Jungle via the
        /video-file/{video_file_id}/upload-video endpoint
        '''
        if upload_method == "file-no-chunk":
            upload_link = self.client._make_request("POST", "/video-file", json={"name": name, "filename": filename, "upload_method": upload_method})
            uploaded = self.client._make_request("POST", f"/video-file/{upload_link['id']}/upload-video", files={"file": filename})
            return self.get(uploaded["id"])
        elif upload_method == "url":
            print("Downloading from URL...")
            return self.client._make_request("POST", "/video-file", json={"name": name, "filename": filename, "upload_method": upload_method})
        
        return self.client._make_request("POST", "/video-file", json={"name": name, "filename": filename, "upload_method": upload_method})
    
    def upload_direct(self, video_file_id, file):
        return self.client._make_request("POST", f"/video-file/{video_file_id}/upload-video", files={"file": file})
    
    def create_analysis(self, video_file_id):
        return self.client._make_request("POST", f"/video-file/{video_file_id}/analysis")

class PromptsAPI:
    def __init__(self, client):
        self.client = client
    
    def list(self):
        obj = self.client._make_request("GET", "/prompts")
        return [Prompt(**prompt) for prompt in obj]
    
    def create(self, prompt: str, parameters: List[str], name: str = "", persona: str = "", task: str = ""):
        obj = self.client._make_request("POST", "/prompts", json={"value": prompt, "parameters": parameters, "persona": persona, "task": task, "name": name})
        return Prompt(**obj)
    
    def generate(self, task: str, parameters: List[str]):
        '''
        Generates a prompt for video generation process
        Parameters is a list of the parameters required by the prompt to generate a video
        IE: ["zodiac sign", "lucky number", "lucky color"] for a horoscope reader
        '''
        res = self.client._make_request("POST", "/prompts/generate", json={"task": task, "parameters": parameters})
        while True:
            prompt = self.get(res["id"])
            if prompt.value != "generating...":
                break
            time.sleep(.2)
            print("Generating prompt...")
        return prompt
    
    def get(self, prompt_id: str):
        obj = self.client._make_request("GET", f"/prompts/{prompt_id}")
        return Prompt(**obj)
    
    def delete(self, prompt_id: str):
        return self.client._make_request("DELETE", f"/prompts/{prompt_id}")
    
class ScriptsAPI:
    def __init__(self, client):
        self.client = client
    
    def list_options(self):
        obj = self.client._make_request("GET", "/scripts")
        return [Script(**script) for script in obj]
    
    def list(self, project_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}/scripts")
        return [Script(**script) for script in obj]
    
    def get(self, project_id: str, script_id: str):
        obj = self.client._make_request("GET", f"/scripts/{project_id}/{script_id}")
        return Script(**obj)
    
    def create(self, project_id: str, name: str, data: dict, inputs: dict):
        obj = self.client._make_request("POST", f"/scripts/{project_id}/scripts", json={"name": name, "data": data, "inputs": inputs})
        return Script(**obj)
    
    def delete(self, project_id: str, script_id: str):
        return self.client._make_request("DELETE", f"/scripts/{project_id}/{script_id}")
    
class UserAPI:
    def __init__(self, client):
        self.client = client 
    
    def info(self):
        obj = self.client._make_request("GET", "/users/me")
        return User(**obj)