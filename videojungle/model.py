from pydantic import BaseModel
from typing import List, Optional, Set
from datetime import time, datetime
from uuid import UUID

class DurationFilter(BaseModel):
    min: float
    max: float

class VideoFilters(BaseModel):
    duration: Optional[DurationFilter] = None
    created_after: Optional[datetime] = None 
    created_before: Optional[datetime] = None
    tags: Optional[List[str]] = None
    min_relevance: Optional[float] = None

    @classmethod
    def create(cls, 
               duration_min: Optional[float] = None,
               duration_max: Optional[float] = None,
               created_after: Optional[datetime] = None,
               created_before: Optional[datetime] = None,
               tags: Optional[List[str]] = None,
               min_relevance: Optional[float] = None) -> Optional['VideoFilters']:
        # Only create filters if we have actual filter values
        has_filters = any([
            duration_min is not None,
            duration_max is not None,
            created_after is not None,
            created_before is not None,
            tags is not None,
            min_relevance is not None
        ])
        
        if not has_filters:
            return None

        duration = None
        if duration_min is not None or duration_max is not None:
            duration = DurationFilter(
                min=duration_min if duration_min is not None else 0,
                max=duration_max if duration_max is not None else float('inf')
            )

        return cls(
            duration=duration,
            created_after=created_after,
            created_before=created_before,
            tags=tags,
            min_relevance=min_relevance
        )

class VideoSearch(BaseModel):
    query: Optional[str] = None
    limit: int = 10
    project_id: Optional[UUID] = None
    filters: Optional[VideoFilters] = None
    include_segments: bool = True
    include_related: bool = False
    query_audio: Optional[str] = None
    query_img: Optional[str] = None

    @classmethod
    def create(cls,
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
               query_img: Optional[str] = None) -> 'VideoSearch':
        
        if duration_min and duration_max and duration_min > duration_max:
            dur = DurationFilter(min=duration_max, max=duration_min)
        else:
            dur = None
        # Create filters if any filter parameters are provided
        filters = VideoFilters(
            duration=dur,
            created_after=created_after,
            created_before=created_before,
            tags=tags,
            min_relevance=min_relevance
        )

        # Convert string project_id to UUID if provided
        uuid_project_id = UUID(project_id) if project_id else None

        return cls(
            query=query,
            limit=limit,
            project_id=uuid_project_id,
            filters=filters,
            include_segments=include_segments,
            include_related=include_related,
            query_audio=query_audio,
            query_img=query_img
        )

class VideoFile(BaseModel):
    id: str
    filename: str
    name: str
    description: Optional[str]
    thumbnail: Optional[str]
    duration: Optional[float]
    fps: Optional[float]
    owner_id: str
    size: Optional[int]
    hash: Optional[str]
    created_at: str
    recorded_at: Optional[str]
    key: str
    analysis: List[dict]
    download_url: Optional[str]
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
    status: Optional[str]
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
