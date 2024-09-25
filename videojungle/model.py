from pydantic import BaseModel, Field
from typing import List, Optional

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
