'''
WIP, not fully implemented
'''
import os
from videojungle import ApiClient

VJ_API_KEY = os.environ['VJ_API_KEY']

vj = ApiClient(token=VJ_API_KEY)

# Define your video task
prompt = vj.prompts.generate(task="a horoscope reader who wants to leave the person excited about their future",
                            parameters=["zodiac sign", "lucky number", "lucky color"])

# Create a project

project = vj.projects.create(name="First Project", description="My first project")
