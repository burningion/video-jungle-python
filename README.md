# Video Jungle API Client

This is a Python client for the Video Jungle API. It provides a simple interface to interact with the Video Jungle API.

## Installation

You can install the Video Jungle API client using pip:

```
pip install videojungle
```

## Usage

Here's a simple example of how to use the Video Jungle API client:

```python
from videojungle import ApiClient

client = ApiClient("your_api_token_here")

# Get a project
project = client.projects.get("2ec097cd-1fff-4824-a7bf-a0e14281f4e5")
print(project)
```

## License

This project is licensed under the MIT License.