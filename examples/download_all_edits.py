from videojungle import ApiClient
import os
from typing import Optional
from datetime import datetime


def download_all_edits(project_id: str, output_dir: str = ".", print_progress: bool = True) -> None:
    """
    Download all rendered video edits from a project.

    Args:
        project_id: UUID of the project to download edits from
        output_dir: Directory to save downloaded videos (default: current directory)
        print_progress: Whether to print download progress (default: True)
    """
    # Initialize API client
    vj_api_key = os.environ.get('VJ_API_KEY')
    if not vj_api_key:
        raise ValueError("VJ_API_KEY environment variable not set")

    vj = ApiClient(token=vj_api_key)

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # List all edits in the project
    if print_progress:
        print(f"Fetching edits for project {project_id}...")

    edits = vj.edits.list(project_id)

    if not edits:
        print("No edits found in this project.")
        return

    # Sort edits by creation date
    sorted_edits = sorted(edits, key=lambda x: x.get('created_at', ''))

    if print_progress:
        print(f"Found {len(sorted_edits)} edit(s) in the project.")

    # Download each edit with sequential numbering
    for i, edit in enumerate(sorted_edits, 1):
        edit_id = edit.get('id')
        edit_name = edit.get('name', f'edit_{edit_id}')
        created_at = edit.get('created_at', 'unknown')

        # Create episode filename with zero-padded number
        episode_number = str(i).zfill(2)
        output_filename = os.path.join(output_dir, f"episode-{episode_number}.mp4")

        if print_progress:
            print(f"\n[{i}/{len(sorted_edits)}] Downloading: {edit_name}")
            print(f"  Edit ID: {edit_id}")
            print(f"  Created: {created_at}")
            print(f"  Saving to: {output_filename}")

        try:
            vj.edits.download_edit_render(
                project_id=project_id,
                edit_id=edit_id,
                filename=output_filename,
                print_progress=print_progress
            )

            if print_progress:
                print(f"  ✓ Successfully downloaded: {output_filename}")

        except Exception as e:
            print(f"  ✗ Error downloading edit {edit_id}: {str(e)}")
            continue

    if print_progress:
        print(f"\n✓ Download complete! All edits saved to: {output_dir}")


def list_projects_interactive() -> Optional[str]:
    """
    List all projects and allow user to select one.

    Returns:
        Selected project ID or None if cancelled
    """
    vj_api_key = os.environ.get('VJ_API_KEY')
    if not vj_api_key:
        raise ValueError("VJ_API_KEY environment variable not set")

    vj = ApiClient(token=vj_api_key)

    print("Fetching your projects...")
    projects = vj.projects.list()

    if not projects:
        print("No projects found.")
        return None

    print("\nAvailable projects:")
    for i, project in enumerate(projects, 1):
        print(f"{i}. {project.name} (ID: {project.id})")

    while True:
        try:
            choice = input("\nEnter project number (or 'q' to quit): ").strip()

            if choice.lower() == 'q':
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(projects):
                return projects[idx].id
            else:
                print(f"Please enter a number between 1 and {len(projects)}")

        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None


if __name__ == "__main__":
    import sys

    # Check if project ID was provided as command line argument
    if len(sys.argv) > 1:
        project_id = sys.argv[1]
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "./downloaded_edits"
    else:
        # Interactive mode: list projects and let user choose
        project_id = list_projects_interactive()
        if not project_id:
            print("No project selected. Exiting.")
            sys.exit(0)

        output_dir = input("Enter output directory (press Enter for './downloaded_edits'): ").strip()
        if not output_dir:
            output_dir = "./downloaded_edits"

    # Download all edits
    download_all_edits(project_id=project_id, output_dir=output_dir, print_progress=True)
