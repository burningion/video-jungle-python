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
    "video_output_filename": "output_video.mp4",
    "video_series_sequential": [
        {
            "video_id": "31341e7e-c173-45a7-ab2d-5196c8ec7dea",
            "type": "videofile",
            "video_start_time": "00:00:00",
            "video_end_time": "00:00:04.6",
            "audio_levels": [
                {
                    "audio_level": "0.5",
                    "start_time": "00:00:00",
                    "end_time": "00:00:04.6"
                }
            ]
        },
        {
            "video_id": "d70c41ab-4d27-4e64-846f-22313a05f627",
            "type": "videofile",
            "video_start_time": "00:00:00",
            "video_end_time": "00:00:05.6",
            "audio_levels": [
                {
                    "audio_level": "0.5",
                    "start_time": "00:00:00",
                    "end_time": "00:00:05.6"
                }
            ]
        },
        {
            "video_id": "f024b9d6-a255-4a1d-a257-5758dc631c34",
            "type": "videofile",
            "video_start_time": "00:00:00",
            "video_end_time": "00:00:01.6",
            "audio_levels": [
                {
                    "audio_level": "0.5",
                    "start_time": "00:00:00",
                    "end_time": "00:00:01.6"
                }
            ]
        }
    ],
    "audio_overlay": []
}

# Create the video edit, must be associated with a project

project_id = "a9c7c17a-cb15-40a8-9ee3-617922c8a827"

# Edit will be an asset, with a url we can check

edit = vj.projects.render_edit(project_id, video_edit)

# Print out the URL to the edit

print(edit.url)
