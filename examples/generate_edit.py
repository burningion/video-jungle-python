from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Create a project or use an existing one
project = vj.projects.create(name="My Project", description="This is a test project")
project_id = project.id

# Upload a video file from local computer
video = vj.video_files.create(name="Kirk Upload", filename="/Users/stankley/Video/50spin.mp4")

# Now we have a VideoFile object, can use it's id in a basic edit
# Subtitles are enabled by default (subtitles=True)
# To disable subtitles, explicitly set subtitles=False
edit  = vj.edits.create_edit_from_clips(project_id=project_id, 
                                        name="program generated edit", 
                                        description="three clip edit",
                                        skip_rendering=True, # don't render yet! set this to False to render
                                        subtitles=True, # Explicitly enable subtitle generation (this is the default)
                                        # subtitles=False, # Uncomment this line to disable subtitles
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
vj.edits.open_in_browser(project_id, edit['edit_id'])

# Now render the edit
vj.edits.download_edit_render(project_id, edit["edit_id"], "out.mp4", True)