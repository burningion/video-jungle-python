from videojungle import ApiClient
import typer
import time
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

app = typer.Typer()

@app.command()
def analyze_video(url: str, name: str):
    # Let's download an analyze a video from YouTube
    video = vj.video_files.create(name, url, "url")
    print(video)

    print(f"Video ID: {video['video']['id']}")

    # Pipeline will begin downloading an analyzing video
    print("downloading video...")
    # Wait for the video to be analyzed

    # Get rid of this sleep later
    time.sleep(20)

    print(f"Video File download analysis: {vj.video_files.get(video['video']['id'])}")

if __name__ == "__main__":
    app()
