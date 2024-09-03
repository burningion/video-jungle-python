from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Define your video generation task, along with variables to pass on generation
prompt = vj.prompts.generate(task="a horoscope reader who wants to leave the person excited about their future",
                            parameters=["zodiac sign", "lucky number", "lucky color"])

# Print out the generated prompt
print(prompt.value)

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
                                         "lucky number": "7",
                                         "lucky color": "green"})
print(video)

# Get the video file ID from the generated video
asset_id = video["asset_id"]

# Save the video file to disk, automatically waits for generation
print(f"Generating video with asset id: {asset_id}")
video_file = vj.assets.download(asset_id, "generated_horoscope.mp4")
print(f"Video generated and saved to: {video_file}")