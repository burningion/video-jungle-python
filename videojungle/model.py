from pydantic import BaseModel
from typing import List, Optional
from datetime import time
from uuid import UUID

class VideoFile(BaseModel):
    id: str
    filename: str
    name: str
    description: Optional[str]
    thumbnail: str
    duration: float
    fps: float
    owner_id: str
    size: int
    hash: str
    created_at: str
    recorded_at: Optional[str]
    key: str
    analysis: List[dict]
    # embeddings: List[dict]

class VideoAudioLevel(BaseModel):
    audio_level: float
    start_time: Optional[time]
    end_time: Optional[time]

class VideoEditAudioAsset(BaseModel):
    audio_id: UUID
    type: str
    audio_start_time: Optional[time]
    audio_end_time: Optional[time]
    audio_levels: List[VideoAudioLevel]

class VideoEditAsset(BaseModel):
    video_id: UUID
    type: str
    video_start_time: time
    video_end_time: Optional[time]
    audio_levels: List[VideoAudioLevel]

class VideoEditCreate(BaseModel):
    video_edit_version: str
    video_output_format: str
    video_output_resolution: str
    video_output_fps: float
    video_output_filename: str
    video_series_sequential: List[VideoEditAsset]
    audio_overlay: List[VideoEditAudioAsset]

class User(BaseModel):
    id: str
    email: str
    name: str
    avatar: str
    is_verified: bool
    is_active: bool

class Script(BaseModel):
    id: str
    project_id: str
    value: dict
    inputs: List[dict]
    name: str
    created_at: str 

class Prompt(BaseModel):
    id: str
    value: str
    persona: str
    created_at: str
    parameters: List[str]
    name: str
    task: Optional[str]

class Asset(BaseModel):
    id: str
    keyname: str
    url: Optional[str]
    download_url: Optional[str]
    asset_path: Optional[str]
    asset_type: str
    created_at: str
    status: str
    uploaded: bool

class Project(BaseModel):
    id: str
    name: str
    description: Optional[str]
    data: Optional[str]
    created_at: str
    owner_id: str
    asset_count: int
    assets: List[Asset]
    prompts: List[dict]
    scripts: List[Script]
