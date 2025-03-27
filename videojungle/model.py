from pydantic import BaseModel, Field
from typing import List, Optional, Set
from datetime import time, datetime
from uuid import UUID

class DurationFilter(BaseModel):
    """Model representing duration filter constraints for video search."""
    min: float = Field(
        ...,
        title="Minimum Duration",
        description="The minimum duration in seconds for filtering videos.",
    )
    max: float = Field(
        ...,
        title="Maximum Duration",
        description="The maximum duration in seconds for filtering videos.",
    )

class VideoFilters(BaseModel):
    """Model representing various filtering options for video search."""
    duration: Optional[DurationFilter] = Field(
        None,
        title="Duration Filter",
        description="Filter for video duration constraints.",
    )
    created_after: Optional[datetime] = Field(
        None,
        title="Created After",
        description="Filter for videos created after this datetime.",
    )
    created_before: Optional[datetime] = Field(
        None,
        title="Created Before",
        description="Filter for videos created before this datetime.",
    )
    tags: Optional[List[str]] = Field(
        None,
        title="Tags",
        description="Filter videos by specific tags.",
    )
    min_relevance: Optional[float] = Field(
        None,
        title="Minimum Relevance",
        description="Minimum relevance score for filtered results.",
    )

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
    """Model representing video search parameters and filters."""
    query: Optional[str] = Field(
        None,
        title="Search Query",
        description="Text search query for finding videos.",
    )
    limit: int = Field(
        10,
        title="Result Limit",
        description="Maximum number of results to return.",
        ge=1,
    )
    project_id: Optional[UUID] = Field(
        None,
        title="Project ID",
        description="UUID of the project to scope the search.",
    )
    filters: Optional[VideoFilters] = Field(
        None,
        title="Search Filters",
        description="Additional filtering criteria for the search.",
    )
    include_segments: bool = Field(
        True,
        title="Include Segments",
        description="Whether to include video segments in results.",
    )
    include_related: bool = Field(
        False,
        title="Include Related",
        description="Whether to include related videos in results.",
    )
    query_audio: Optional[str] = Field(
        None,
        title="Audio Query",
        description="Search query for audio content.",
    )
    query_img: Optional[str] = Field(
        None,
        title="Image Query",
        description="Search query for image content.",
    )

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

class VideoUpload(BaseModel):
    """Model representing a video file upload."""
    name: str = Field(
        ...,
        title="Video Name",
        description="Name of the video file.",
    )
    filename: str = Field(
        ...,
        title="Filename",
        description="Filename of the video file, or a URL to download the video.",
    )
    upload_method: Optional[str] = Field(
        "file-no-chunk", # defaults to uploading a local file
        title="Upload Method",
        description="Method to use for uploading the video file. (e.g., 'file-no-chunk', 'direct', 'url').",
    )

class VideoAudioLevel(BaseModel):
    """Model representing audio level measurements for a video segment."""
    audio_level: float = Field(
        ...,
        title="Audio Level",
        description="The measured audio level value in decimal format (0..1).",
    )
    start_time: Optional[time] = Field(
        None,
        title="Start Time",
        description="The starting timestamp of this audio level measurement in 00:00:00.000 format.",
    )
    end_time: Optional[time] = Field(
        None,
        title="End Time",
        description="The ending timestamp of this audio level measurement in 00:00:00.000 format.",
    )

class VideoEditAudioAsset(BaseModel):
    """Model representing an audio asset that can be overlaid on a video edit."""
    audio_id: UUID = Field(
        ...,
        title="Audio Asset ID",
        description="Unique identifier for the audio asset.",
    )
    type: str = Field(
        ...,
        title="Asset Type",
        description="The type of audio asset (e.g., 'music', 'voiceover', 'sound_effect').",
    )
    audio_start_time: Optional[time] = Field(
        None,
        title="Audio Start Time",
        description="The timestamp where this audio asset should start playing.",
    )
    audio_end_time: Optional[time] = Field(
        None,
        title="Audio End Time",
        description="The timestamp where this audio asset should stop playing.",
    )
    audio_levels: List[VideoAudioLevel] = Field(
        ...,
        title="Audio Levels",
        description="List of audio level measurements for this asset.",
    )

class VideoEditAsset(BaseModel):
    """Model representing a video asset in an edit sequence."""
    video_id: UUID = Field(
        ...,
        title="Video UUID",
        description="Unique identifier for the video asset.",
    )
    type: str = Field(
        ...,
        title="Asset Type",
        description="The type of video asset (e.g., 'videofile', 'asset', etc.).",
    )
    video_start_time: time = Field(
        ...,
        title="Video Start Time",
        description="The timestamp where this video segment should start in 00:00:00.000 format.",
    )
    video_end_time: Optional[time] = Field(
        None,
        title="Video End Time",
        description="The timestamp where this video segment should end in 00:00:00.000 format.",
    )
    audio_levels: List[VideoAudioLevel] = Field(
        ...,
        title="Audio Levels",
        description="List of audio level measurements for this video segment (0..1).",
    )

class VideoEditCreate(BaseModel):
    """Model representing the creation parameters for a video edit."""
    name: Optional[str] = Field(
        None,
        title="Name of edit",
        descripton="Name of editing project"
    )
    description: Optional[str] = Field(
        None,
        title="Description of edit",
        description="Natural language description of the edit."
    )
    video_edit_version: str = Field(
        ...,
        title="Edit Version",
        description="Version identifier for this edit configuration.",
    )
    video_output_format: str = Field(
        ...,
        title="Output Format",
        description="The desired output video format (e.g., 'mp4', 'mov').",
    )
    video_output_resolution: str = Field(
        ...,
        title="Output Resolution",
        description="The desired output resolution (e.g., '1920x1080', '1080x1920').",
    )
    video_output_fps: float = Field(
        ...,
        title="Output FPS",
        description="The desired output frames per second.",
    )
    video_output_filename: str = Field(
        ...,
        title="Output Filename",
        description="The desired filename for the output video.",
    )
    video_series_sequential: List[VideoEditAsset] = Field(
        ...,
        title="Video Sequence",
        description="Ordered list of video assets that make up the edit.",
    )
    audio_overlay: List[VideoEditAudioAsset] = Field(
        ...,
        title="Audio Overlays",
        description="List of audio assets to overlay on the video sequence.",
    )

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
