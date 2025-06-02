# Video Jungle Examples

This directory contains examples of projects using the Video Jungle API to create generative videos:

[analyze_video.py](./analyze_video.py) - CLI to download a video from a URL and analyze it for search and retrieval. (Requires [typer](https://typer.tiangolo.com/): `pip install typer`)

[create_project_with_template.py](./create_project_with_template.py) - Create a project with a specific script template key to determine the generation flow.

[generate_edit.py](./generate_edit.py) - Generate a video edit from a set of VideoFiles

[generate_horoscope.py](./generate_horoscope.py) - Creates a horoscope generator that takes in a date, zodiac sign, and lucky number for video horoscope generation.

[generate_iching.py](./generate_iching.py) - Create an I Ching Reader which throws a virtual set of coins to read you an answer to your question. (Requires [questionary](https://questionary.readthedocs.io/en/stable/):`pip install questionary`)

[voice-overlay.py](./voice-overlay.py) - Search the web for the latest episode of "The Rehearsal", create some interesting topics, and then generate a voiceover prompt template project to create a found footage video edit with a voice overlay. Run via `uv run voice-overlay.py`, the script dependencies are declared within the file.
