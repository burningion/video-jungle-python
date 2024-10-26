from videojungle import ApiClient
import time
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Let's download an analyze a video from YouTube
video = vj.video_files.create("Skate Submarine", "https://www.youtube.com/watch?v=aAREp5P3mE4", "url")

print(video)

print(f"Video ID: {video['video']['id']}")

# Pipeline will begin downloading an analyzing video
print("downloading video...")
# Wait for the video to be analyzed

# Get rid of this sleep later
time.sleep(20)

print(f"Video File download analysis: {vj.video_files.get(video['video']['id'])}")

