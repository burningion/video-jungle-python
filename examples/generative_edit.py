# We also require instructor and pydantic for this example
# $ pip install instructor[anthropic] pydantic 
# to install the instructor package
from videojungle import ApiClient
import os
import random

from typing import List
import instructor
from anthropic import Anthropic # Assumes you've set your API key as an environment variable
from pydantic import BaseModel

vj = ApiClient(token=os.environ['VJ_API_KEY'])

# Let's search the web for some up to date Nathan Fielder episode topics / controversies
# and generate paramters for our prompt

class ClipParameters(BaseModel):
    clip_topics: List[str]
    latest_episode_topic: str

client = instructor.from_anthropic(Anthropic())

search_prompt = """
I'm trying to come up with an interesting spoken dialogue prompt about nathan fielder's the rehearsal. 
can you help me come up with ideas for what might be interesting? you can search the web to get up to date info.
don't give me a summary of the show, or the show as a topic. instead just give me a list of topics or controversies that might be interesting to discuss.
the latest episode topic should be a paragraph or two about the latest episode, and the clip topics should be a list of 5-10 topics that are interesting to discuss.
"""

resp = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": search_prompt,
        }
    ],
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5
    }],
    response_model=ClipParameters,
)

print(f"latest episode topic: {resp.latest_episode_topic}")
print("clip topics: ")
for topic in resp.clip_topics:
    print(f"- {topic}")

# First, let's list the types of generative media we can create
# on video jungle (e.g. prompt-to-video, prompt-to-speech, etc.)
# This will list all the generative media options available in your account
generative_media = vj.scripts.list_options()

print("Generative media options:")
for media in generative_media:
    print(f"- {media.key}: {media.description}")

# For this example, we'll use the key for generating a voiceover
# (Would otherwise be media.key) from our list above
script_key = "prompt-to-speech" 

# A prompt is used to describe the generative task you want to perform
prompt = vj.prompts.generate(task="You are a Nathan Fielder episode analyzer, picking a meta idea to discuss. You aim for 30 second clips that are funny and insightful.",
                            parameters=["clip topic", "latest episode topic"])

# Now we can create a project to hold our generated media
project = vj.projects.create(name="Nathan Fielder Clips", description="Clips from Nathan Fielder episodes", prompt_id=prompt.id, generation_method=script_key)
# Grab the script ID from the project for prompt-to-speech generation
script_id = project.scripts[0].id
print(f"Created project: {project.name} with ID: {project.id} and script ID: {script_id}")

# Pick a random topic from the list of clip topics
topic = random.choice(resp.clip_topics)
print(f"Selected topic: {topic}")
# We can now generate a prompt-to-speech asset:
video = vj.projects.generate(script_id=script_id, 
                              project_id=project.id,
                              parameters={"clip topic": topic,
                                          "latest episode topic": resp.latest_episode_topic})
print(f"Generated voiceover from topics with asset id: {video['asset_id']}")
# Save the audio file to disk, automatically waits for generation
audio_file = vj.assets.download(video["asset_id"], "generated_nathan_fielder.mp3")