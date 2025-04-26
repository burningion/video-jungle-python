from .client import ApiClient
from .model import VideoSearch, VideoFile, VideoEditAsset, VideoEditAudioAsset, VideoFilters, VideoEditCreate, VideoUpload

try:
    from importlib.metadata import version
    __version__ = version("videojungle")
except ImportError:
    __version__ = "unknown"