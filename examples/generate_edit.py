from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Let's do a manual video edit
# Your video edit will need to have your own, appropriate video IDs

video_edit = {
    "video_edit_version": "1.0",
    "video_output_format": "mp4",
    "video_output_resolution": "1920x1080",
    "video_output_fps": 30.0,
    "video_output_filename": "my_video_edit.mp4",
    "video_series_sequential": [
        {
            "video_id": "123e4567-e89b-12d3-a456-426614174000",
            "type": "videofile",
            "video_start_time": "00:00:00",
            "video_end_time": "00:00:10",
            "audio_levels": [
                {
                    "audio_level": 0.5,
                    "start_time": "00:00:00",
                    "end_time": "00:00:10"
                }
            ]
        },
        {
            "video_id": "123e4567-e89b-12d3-a456-426614174001",
            "type": "videofile",
            "video_start_time": "00:00:10",
            "video_end_time": "00:00:20",
            "audio_levels": [
                {
                    "audio_level": 0.7,
                    "start_time": "00:00:10",
                    "end_time": "00:00:20"
                }
            ]
        }
    ],
    "audio_overlay": [
        {
            "audio_id": "123e4567-e89b-12d3-a456-426614174002",
            "type": "audio",
            "audio_start_time": "00:00:00",
            "audio_end_time": "00:00:20",
            "audio_levels": [
                {
                    "audio_level": 0.5,
                    "start_time": "00:00:00",
                    "end_time": "00:00:20"
                }
            ]
        }
    ]
}

# Create the video edit, must be associated with a project

project_id = "123e4567-e89b-12d3-a456-426614174003"

# Edit will be an asset, with a url we can check

edit = vj.projects.render_edit(project_id, video_edit)

# Print out the URL to the edit

print(edit.url)
