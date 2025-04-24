# Video Jungle API Client

This is a Python client for the [Video Jungle API](https://docs.video-jungle.com/). 

[Video Jungle](https://www.video-jungle.com/) is a generative video creator. It allows you to generate custom videos via dynamic variables.

Let's say you want to generate daily astrology readings according to your user's astrological sign, lucky number, and lucky color.

Video Jungle allows you to pass in a value for each, and generate a unique video for that specific user.

See below for an example of how to build a generative video workflow using the API.

## Installation

You can install the Video Jungle API client using pip:

```
pip install videojungle
```

## Usage

Here's a simple example of how to use the Video Jungle API client for the Horoscope example:

```python
from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Define your video generation task, along with variables to pass on generation
prompt = vj.prompts.generate(task="a horoscope reader who wants to leave the person excited about their future",
                            parameters=["zodiac sign", "lucky number", "date"])

# Alternatively, create your own prompt:
# prompt = vj.prompts.create(prompt="generate a horoscope for ${ZODIAC SIGN}, with lucky number ${LUCKY NUMBER} on ${DATE}",
#                            parameters=["ZODIAC SIGN", "LUCKY NUMBER", "DATE"], name="Horoscope Reader", task="a horoscope generator",
#                            persona="A psychic squid who sees into the future")

# Print out the generated prompt
print(prompt.value)

# Optionally, list out scripts available as generation methods
scripts = vj.scripts.list_options()
print(scripts)

# Create a project to hold generated files, using our prompt we've generated
project = vj.projects.create(name="First Project", description="My first project", prompt_id=prompt.id)

# Get first script for the generation process
# (Scripts define the video generation method from a prompt)
script = project.scripts[0]
script_id = script.id

# Print out parameters required for generation
print(project.prompts[0]['parameters'])

# Generate a video from our created prompt with dynamic variables
video = vj.projects.generate(script_id=script_id, 
                             project_id=project.id,
                             parameters={"zodiac sign": "Aries",
                                         "lucky number": "7", # parameters are always strings
                                         "date": ""2025-04-24""})
print(video)

# Get the video file ID from the generated video
asset_id = video["asset_id"]

# Save the video file to disk, automatically waits for generation
print(f"Generating video with asset id: {asset_id}")
video_file = vj.assets.download(asset_id, "generated_horoscope.mp4")
print(f"Video generated and saved to: {video_file}")
```

This example lives in the `examples/` folder.

## License

This project is licensed under the MIT License.
