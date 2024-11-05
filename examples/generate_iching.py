from videojungle import ApiClient
import os

import random

import questionary

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

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

choice = questionary.select("Would you like to create a new project, or use an existing one?", 
                            choices=["New", "Existing"]).ask()

if choice is None: # CTRL+C
    exit()

if choice == "New":
    name = questionary.text("Enter a project name: ").ask()
    description = questionary.text("Enter a project description: ").ask()
    
    if description is None:
        description = ""
    prompt = vj.prompts.generate(task="You are an AI that performs I Ching readings, relating the hexagram number and changing lines to the user's question",
                            parameters=["question", "number", "changinglines"])

    # See our generated prompt
    print(prompt.value)

    # Optionally, list out scripts available as generation methods
    #scripts = vj.scripts.list_options()
    #print(scripts)

    # Create a project to hold generated files, using our prompt we've generated

    project = vj.projects.create(name=name, description=description, prompt_id=prompt.id)

    # Get first script for the generation process
    # (Scripts define the video generation method from a prompt)
    script = project.scripts[0]
    script_id = script.id
else:
    # Select an existing project
    projects = vj.projects.list()
    project_names = [project.name for project in projects]
    project_name = questionary.select("Select a project", choices=project_names).ask()
    project = next(project for project in projects if project.name == project_name)
    script_id = project.scripts[0].id

question = questionary.text("What is your question?").ask()

answer = build_hexagram(full_hexagram)
print(answer) # (hexagram number, changing lines)


# Print out parameters required for generation
print(project.prompts[0]['parameters'])
print(f"I Ching reading: {answer[0]} with changing lines: {answer[1]}")

# Generate a video from our created prompt with dynamic variables
video = vj.projects.generate(script_id=script_id, 
                             project_id=project.id,
                             parameters={"question": question,
                                         "number": str(answer[0]),
                                         "changinglines": str(answer[1])})

print(video)

# Get the video file ID from the generated video
asset_id = video["asset_id"]

# Save the video file to disk, automatically waits for generation
print(f"Generating video with asset id: {asset_id}")

filename = questionary.text("Enter a filename to save video (Ex: iching.mp4): ").ask()
if not filename:
    filename = "iching.mp4"
video_file = vj.assets.download(asset_id, filename)
print(f"Video generated and saved to: {video_file}")