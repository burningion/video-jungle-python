from videojungle import ApiClient
import os

vj = ApiClient(token=os.environ['VJ_API_KEY'])

# First, let's list the types of generative media we can create
generative_media = vj.scripts.list_options()

print("Generative media options:")
for media in generative_media:
    print(f"- {media.key}: {media.description}")

# For this example, we'll use the key for generating a voiceover
# (Would otherwise be media.key) from our list above
script_key = "prompt-to-speech" 

# A prompt is used to describe the generative task you want to perform
prompt = vj.prompts.generate(task="You are a Nathan Fielder episode analyzer, picking a meta idea to discuss. You aim for 30 second clips that are funny and insightful.",
                            parameters=["clip topic", "latest episode topic", "clip descriptions"])

# Now we can create a project to hold our generated media
project = vj.projects.create(name="Nathan Fielder Clips", description="Clips from Nathan Fielder episodes", prompt_id=prompt.id, generation_method=script_key)

print(f"Created project: {project.name} with ID: {project.id}")