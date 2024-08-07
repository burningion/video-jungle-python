from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

# Define your video generation task, along with variables to pass on generation
prompt = vj.prompts.generate(task="a horoscope reader who wants to leave the person excited about their future",
                            parameters=["zodiac sign", "lucky number", "lucky color"])


# Create a project to hold generated files, using our prompt we've generated
project = vj.projects.create(name="First Project", description="My first project", prompt_id=prompt["id"])

# Get a script for the generation process
script_id = project["script"]["id"]

# Generate a video from our created prompt with dynamic variables
video = project.generate(script_id=script_id, 
                             project_id=project["id"],
                             parameters={"zodiac sign": "Aries",
                                        "lucky number": "7",
                                        "lucky color": "green"})
print(video)