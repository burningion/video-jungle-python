import requests
from urllib import parse
from typing import List, Optional, Any
from .model import VideoFile, Script, Prompt, Project, Asset, User, VideoSearch, VideoFilters, DurationFilter, VideoEditCreate, VideoEditAsset
from .utils import is_youtube_url
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
        self.edits = EditAPI(self)

    def _make_request(self, method, endpoint, **kwargs):
        headers = {
            "X-API-Key": self.token
        }
        if 'headers' in kwargs:
            user_headers = kwargs.pop('headers')
            headers.update(user_headers)

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 422:
                try:
                    error_detail = response.json()
                    print(f"422 Unprocessable Entity: {error_detail}")
                    # This will show the validation errors FastAPI returns
                except ValueError:
                    print("422 Unprocessable Entity: Could not parse error response")
            
            # Re-raise the original exception after printing details
            raise e
    
class ProjectsAPI:
    def __init__(self, client):
        self.client = client

    def get(self, project_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}")
        project = Project(**obj)
        project._client = self.client
        return project
    
    def list(self):
        obj = self.client._make_request("GET", "/projects")
        projects = [Project(**project) for project in obj]
        for project in projects:
            project._client = self.client
        return projects
    
    def create(self, name: str, description: str, prompt_id=None, generation_method: str = "prompt-to-video"):
        if prompt_id:
            project_data = self.client._make_request("POST", "/projects", json={"name": name, "description": description, "prompt_id": prompt_id, "data": generation_method})
        else:
            project_data = self.client._make_request("POST", "/projects", json={"name": name, "description": description, "data": generation_method})
        
        # Use get method which already sets the _client attribute
        return self.get(project_data["id"])
    
    def delete(self, project_id: str):
        return self.client._make_request("DELETE", f"/projects/{project_id}")
    
    def update_project_data(self, project_id: str) -> Project:
        '''
        Updates the project data by fetching the latest information from the server
        Returns the updated project
        '''
        return self.get(project_id)
    
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
    
    def create_edit(self, project_id: str, create_edit: VideoEditCreate):
        '''
        Create a new edit within a project for editing before rendering
        Returns same as above
        '''
        return self.client._make_request("POST", f"/projects/{project_id}/create-edit", json=create_edit.model_dump_json())
    
    def get_edit(self, project_id: str, edit_id: str):
        '''
        Returns an edit from an edit id and a project id
        '''
        return self.client._make_request("GET", f"/projects/{project_id}/edits/{edit_id}")
    
    def list_edits(self, project_id: str):
        '''
        Returns a list of edits within a project
        '''
        return self.client._make_request("GET", f"/projects/{project_id}/edits")


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
    
    def add_videofile_to_project(self, project_id: str, video_file_id: str, description: str = ""):
        # The upload_asset method already updates project data internally
        obj = self.upload_asset(name=video_file_id, description=description, project_id=project_id, filename="", upload_method="video-reference")
        return obj
    
    def upload_asset(self, name: str, description: str, project_id: str, filename: str, upload_method: str = "file-no-chunk"):
        # filetype = detect_file_type(filename)
        if upload_method == "video-reference":
            # name should be uuid of asset
            asset_type = "video-reference"
            link = self.client._make_request("POST", f"/projects/{project_id}/asset", json={"upload_method": upload_method, 
                                                                                               "asset_type": asset_type,
                                                                                               "keyname": name,
                                                                                               "description": description})
            # Update project data after upload
            self.client.projects.update_project_data(project_id)
            return self.get(link['id'])
        if is_youtube_url(filename):
            asset_type = "youtube-url"
        else:
            asset_type = "user"
        
        upload_link = self.client._make_request("POST", f"/projects/{project_id}/asset", json={"upload_method": upload_method, 
                                                                                               "asset_type": asset_type,
                                                                                               "keyname": name,
                                                                                               "description": description})

        # Open the file in binary mode and pass the file object
        with open(filename, 'rb') as file_object:
            uploaded = self.client._make_request("POST", upload_link["upload_url"]["url"], 
                                                files={"file": (filename, file_object)})
        
        # Update project data after upload
        self.client.projects.update_project_data(project_id)
        return self.get(uploaded["id"])
    
    def add_asset_from_video_file(self, video_file_id: str, project_id: str, start_time: Optional[float] = None, end_time: Optional[float] = None):
        # TODO: Implement this method
        pass

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
    
    def create(self, name: str, filename: str, upload_method: str = "file-no-chunk", run_analysis: bool = True):
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
            with open(filename, 'rb') as file_obj:
                uploaded = self.client._make_request("POST", f"/video-file/{upload_link['video']['id']}/upload-video", files={"file": file_obj})
            if run_analysis:
                self.client._make_request("POST", f"/video-file/{uploaded['id']}/analysis")
            return self.get(uploaded["id"])
        elif upload_method == "url":
            print("Downloading from URL...")
            return self.client._make_request("POST", "/video-file", json={"name": name, "filename": filename, "upload_method": upload_method})
        
        if run_analysis:
            vf = self.client._make_request("POST", "/video-file", json={"name": name, "filename": filename, "upload_method": upload_method})
            self.client._make_request("POST", f"/video-file/{vf['id']}/analysis")
            return vf
        else:
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
    
class EditAPI:
    def __init__(self, client):
        self.client = client

    def get_edit_schema(self) -> dict[str, Any]:
        '''
        Get the schema for the edit object
        Returns a JSON schema   
        '''
        return VideoEditCreate.model_json_schema()

    def create_edit(self, project_id: str, create_edit: VideoEditCreate):
        '''
        Create a new edit within a project for editing before rendering
        Returns same as above
        '''
        return self.client._make_request("POST", f"/projects/{project_id}/create-edit", data=create_edit.model_dump_json(),
                                         headers={"Content-Type": "application/json"})

    def create_edit_from_clips(
                    self, 
                    project_id: str, 
                    clips: list[dict],
                    name: str = "",
                    description: str = "",
                    output_format: str = "mp4",
                    output_resolution: str = "1920x1080",
                    output_fps: float = 30.0,
                    skip_rendering: bool = False
                ) -> dict:
        """
        Create a video edit with multiple clips.
        
        Args:
            project_id: Project ID
            clips: List of clip dictionaries, each containing:
                - video_id: Video UUID (string)
                - type: Asset type (string, default: "videofile")
                - start_time: Start time in 00:00:00.000 format (string)
                - end_time: End time in 00:00:00.000 format (string)
            name: Optional name for the edit
            description: Optional description for the edit
            output_format: Output format (default: mp4)
            output_resolution: Output resolution (default: 1920x1080)
            output_fps: Output frames per second (default: 30.0)
            
        Returns:
            Response from the API
        """
        
        # Create video series from clips
        video_series = []
        for clip in clips:
            # Get clip details with defaults
            video_id = clip.get("id")
            clip_type = clip.get("type", "videofile")
            start_time = clip.get("start_time")
            end_time = clip.get("end_time")
            
            # Validate required fields
            if not video_id:
                raise ValueError("Each clip must include an id")
            if not start_time:
                raise ValueError("Each clip must include a start_time")
            if not end_time:
                raise ValueError("Each clip must include an end_time")
                
            # Convert string UUID to UUID object if needed
            try:
                video_uuid = UUID(video_id) if isinstance(video_id, str) else video_id
            except ValueError:
                raise ValueError(f"Invalid id: {video_id}")
            
            # Create video asset
            video_asset = VideoEditAsset(
                video_id=video_uuid,
                type=clip_type,
                video_start_time=start_time,
                video_end_time=end_time,
                audio_levels=[]  # Empty list as default
            )
            
            video_series.append(video_asset)
        
        # Create the edit object
        edit = VideoEditCreate(
            name=name,
            description=description,
            video_edit_version="1.0",
            video_output_format=output_format,
            video_output_resolution=output_resolution,
            video_output_fps=output_fps,
            video_output_filename=f"{name or 'video'}.{output_format}",
            video_series_sequential=video_series,
            audio_overlay=[],  # Empty list as default
            skip_rendering=skip_rendering  # If true don't render yet
        )
    
        return self.create_edit(project_id, edit)
        
    def get(self, project_id: str, edit_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}/edits/{edit_id}")
        return obj
    
    def open_in_browser(self, project_id: str, edit_id: str):
        """
        Open the edit in the browser.
        """
        url = f"https://app.video-jungle.com/projects/{project_id}/edits/{edit_id}"
        import webbrowser
        webbrowser.open(url)
        return
    
    def list(self, project_id: str):
        obj = self.client._make_request("GET", f"/projects/{project_id}/edits")
        return obj
    
    def render_edit(self, project_id: str, edit_id: str) -> dict:
        """
        Returns a dictionary with asset_id, asset_key, and original edit_id
        """
        return self.client._make_request("POST", f"/projects/{project_id}/edits/{edit_id}/render")
    
    def download_edit_render(self, project_id: str, edit_id: str, filename: str, print_progress: bool = False):
        """
        Download an edit render, rendering and waiting for rendered file if
        not already rendered. Optionally print progress to console.se
        """

        edit = self.get(project_id=project_id, edit_id=edit_id)
        print(edit)
        download_url = edit.get("download_url")

        if not download_url:
            render = self.render_edit(project_id=project_id, edit_id=edit_id)
            asset_id = render["asset_id"]

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