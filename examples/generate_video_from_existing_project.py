from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Button, SelectionList, Label
from textual.binding import Binding
from textual import events

from typing import List

from videojungle import ApiClient
import os

# Assumes you've set your API key as an environment variable
VJ_API_KEY = os.environ['VJ_API_KEY']

# Initialize API client
vj = ApiClient(token=VJ_API_KEY)

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

    def __init__(self, projects: List[str]):
        super().__init__()
        self.projects = projects

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="project-container"):
            yield Label("Select a Project", id="title")
            yield SelectionList[str](
                *((project, project) for project in self.projects),
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
            print(f"Selected project: {selection[0]}")
            self.exit(selection[0])

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

def select_project(projects: List[str]) -> str:
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

    projects = vj.projects.list()
    sample_projects = [project.name for project in projects]
    
    selected = select_project(sample_projects)
    if selected:
        print(f"You selected: {selected}")
    else:
        print("Selection cancelled")