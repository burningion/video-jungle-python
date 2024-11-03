from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, SelectionList, Label, Input
from textual.binding import Binding
from textual.screen import Screen
from textual import events

from typing import List

from videojungle import ApiClient
from videojungle.model import Project
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

class VideoGenerationScreen(Screen):
    """Screen for configuring and starting video generation."""
    def __init__(self, project: Project):
        super().__init__()
        self.project = project
    
    def compose(self) -> ComposeResult:
        variables = self.project.prompts[0]['parameters']
        yield Header()
        yield Container(
            Label(f"Generating video for {self.project.name}", id="project-info"),
        )
        with Container(id="video-gen-form"):
            yield Label("Parameters:")
            for name in variables:
                yield Input(name, id=name.replace(" ", "-"))
        yield Container(
            Button("Generate", id="generate_btn"),
            Button("Back", id="back_btn"),
            id="actions"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate_btn":
            self.generate_video()
        elif event.button.id == "back_btn":
            self.app.pop_screen()

    def generate_video(self) -> None:
        params = {name: self.query_one(f"#{name.replace(' ', '-')}").value for name in self.project.prompts[0]['parameters']}
        # Add API call to generate video here
        self.notify(f"Starting video generation with parameters: {params}")

class ProjectSelector(App):
    """A Textual application for selecting projects."""
    
    CSS = """
    Screen {
        align: center middle;
    }

    #project-container {
        width: 60%;
        height: 70%;
        border: heavy $accent;
        padding: 1 2;
    }

    #title {
        content-align: center middle;
        text-style: bold;
        margin: 1 0;
    }

    SelectionList {
        height: 80%;
        border: tall $panel;
        margin: 1 0;
    }

    #button-container {
        height: auto;
        align: center middle;
        margin: 1 0;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("enter", "select", "Select", show=True),
    ]

    SCREENS = {"video_gen": VideoGenerationScreen}

    def __init__(self, projects: List[Project]):
        super().__init__()
        self.projects = projects

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="project-container"):
            yield Label("Select a Project", id="title")
            yield SelectionList[str](
                *((project.name, project.name) for project in self.projects),
                id="project-list"
            )
            with Container(id="button-container"):
                yield Button("Select", variant="primary", id="select-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "select-btn":
            self.action_select()
        elif event.button.id == "cancel-btn":
            self.action_quit()

    def action_select(self) -> None:
        """Handle project selection."""
        selection = self.query_one("#project-list").selected
        if selection:
            # You can modify this to handle the selection however you need
            print(f"Selected project: {selection}")
            project_name = selection[0]
            selected_project = next(p for p in self.projects if p.name == project_name)
            self.push_screen(VideoGenerationScreen(selected_project))

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

def select_project(projects: List[Project]) -> str:
    """
    Run the project selector application.
    
    Args:
        projects: List of project names to display
        
    Returns:
        Selected project name or None if cancelled
    """
    app = ProjectSelector(projects)
    return app.run()

if __name__ == "__main__":

    sample_projects = vj.projects.list()
    selected = select_project(sample_projects)
    if selected:
        print(f"You selected: {selected}")
    else:
        print("Selection cancelled")