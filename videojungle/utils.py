import re
import mimetypes

# Make sure MIME types are initialized
mimetypes.init()

def detect_file_type(file_path):
    """
    Detect if a file is an image, audio, or video based on its mimetype.
    Returns a tuple of (file_type, mime_type)
    """
    # Get the MIME type based on file extension
    mime_type, encoding = mimetypes.guess_type(file_path)
    
    # If mimetype couldn't be determined by extension
    if mime_type is None:
        return "unknown", None
    
    # Check the main type
    main_type = mime_type.split('/')[0]
    
    if main_type == 'image':
        return "image", mime_type
    elif main_type == 'audio':
        return "audio", mime_type
    elif main_type == 'video':
        return "video", mime_type
    else:
        return "other", mime_type

def is_youtube_url(string):
    # Pattern to match common YouTube URL formats
    youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/|v\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    
    # Search for the pattern in the string
    match = re.search(youtube_pattern, string)
    
    # Return True if found, False otherwise
    return match is not None
