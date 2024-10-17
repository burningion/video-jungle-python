from videojungle import ApiClient
import os

import random

# Code for I Ching reading
# https://en.wikipedia.org/wiki/I_Ching
lines = {
    ("heads", "heads", "heads"): "yang (moving line)",
    ("heads", "heads", "tails"): "yin (broken line)",
    ("heads", "tails", "tails"): "yang (solid line)",
    ("tails", "tails", "tails"): "yin (moving line)"
}

def interpret_toss(toss):
    print(f"{toss} {lines.get(toss)}")
    if toss == ('heads', 'heads', 'heads'):
        return 1, True # Yang, moving line
    elif toss == ('heads', 'heads', 'tails'):
        return 1, False # Yang, solid line
    elif toss == ('heads', 'tails', 'tails'):
        return 0, False # Yin, solid line
    elif toss == ('tails', 'tails', 'tails'):
        return 0, True  # Yin, moving line
    

def build_hexagram(toss_results):
    lines = []
    changing_lines = []

    for idx, toss in enumerate(toss_results):
        line, is_changing = interpret_toss(toss)
        lines.append(line)
        if is_changing:
            changing_lines.append(idx + 1)

    hexagram_binary = lines[::-1] # bottom to top
    hexagram_number = int(''.join(map(str, hexagram_binary)), 2)
    return hexagram_number +  1, changing_lines

def throw_coins():
    a = [random.choice(["heads", "tails"]) for i in range(3)]
    a.sort()
    return tuple(a)

full_hexagram = []
for i in range(6):
    full_hexagram.append(throw_coins())

answer = build_hexagram(full_hexagram)
print(answer) # (hexagram number, changing lines)

# Now, let's make a video from this

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

prompt = vj.prompts.generate(task="You are an AI that performs I Ching readings.",
                            parameters=["question", "number", "changinglines"])

# See our generated prompt
print(prompt.value)

# Optionally, list out scripts available as generation methods
#scripts = vj.scripts.list_options()
#print(scripts)

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
                             parameters={"question": "What is the meaning of life?",
                                         "number": answer[0],
                                         "changinglines": str(answer[1])})

print(video)

# Get the video file ID from the generated video
asset_id = video["asset_id"]

# Save the video file to disk, automatically waits for generation
print(f"Generating video with asset id: {asset_id}")
video_file = vj.assets.download(asset_id, "generated_horoscope.mp4")
print(f"Video generated and saved to: {video_file}")