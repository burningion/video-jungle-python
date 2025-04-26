from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Create a project or use an existing one
project_id = "e517d9ae-f4e4-4319-86a9-76f46e48b8a2"
# Upload a video file from local computer
video = vj.video_files.create(name="Kirk Upload", filename="/Users/stankley/Video/50spin.mp4")

# Now we have a VideoFile object, can use it's id in a basic edit
edit  = vj.edits.create_edit_from_clips(project_id=project_id, 
                                        name="program generated edit", 
                                        description="three clip edit",
                                        clips=[{"start_time": "00:00:10.000", 
                                                "end_time": "00:00:15.000", 
                                                "type": "videofile", 
                                                "video_id": video.id}, 
                                                {"start_time": "00:00:10.000",
                                                "end_time": "00:00:15.000",
                                                "type": "videofile", 
                                                "video_id": video.id}
                                                ])

# Now we can open it in a browser
vj.edits.open_in_browser(project_id, edit['id'])