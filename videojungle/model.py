from pydantic import BaseModel, Field
from typing import List, Optional

class VideoFile(BaseModel):
    id: str
    filename: str
    name: str
    description: str
    thumbnail: str
    duration: float
    fps: int
    owner_id: str
    size: int
    hash: str
    created_at: str
    recorded_at: str
    key: str
    analysis: dict
    embeddings: List[dict]

'''
'''

class Script(BaseModel):
    id: str
    project_id: str
    value: str
    inputs: dict
    name: str
    created_at: str 

class Prompt(BaseModel):
    id: str
    value: str
    persona: str
    created_at: str
    parameters: List[str]
    name: str
    task: str

class Project(BaseModel):
    id: str
    name: str
    description: str
    data: dict
    created_at: str
    owner_id: str
    asset_count: int
    assets: List[VideoFile]
    prompts: List[dict]
    scripts: List[Script]

class Asset(BaseModel):
    id: str
    keyname: str
    url: str
    download_url: str
    project: dict
    asset_path: str
    asset_type: str
    created_at: str
    status: str
    uploaded: bool