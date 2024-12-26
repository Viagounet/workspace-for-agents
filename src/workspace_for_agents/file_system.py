import os
from typing import Optional, Self


class File:
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name

    def __repr__(self) -> str:
        return f"File(path={self.path}, name={self.name})"


class Folder:
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        self.files: list[File] = []
        self.subfolders: list[Folder] = []

    def add_file(self, file: File):
        self.files.append(file)

    def add_subfolder(self, folder: Self):
        self.subfolders.append(folder)

    def tree(self, indent: str = "") -> str:
        """Returns a string representation of the folder structure in tree format"""
        result = [f"{indent}{self.name}/"]

        for i, file in enumerate(sorted(self.files, key=lambda f: f.name)):
            is_last_file = (i == len(self.files) - 1) and len(self.subfolders) == 0
            if is_last_file:
                result.append(f"{indent}└── {file.name}")
            else:
                result.append(f"{indent}├── {file.name}")

        for i, subfolder in enumerate(sorted(self.subfolders, key=lambda f: f.name)):
            is_last = i == len(self.subfolders) - 1
            if is_last:
                result.append(subfolder.tree(indent + "    "))
            else:
                result.append(subfolder.tree(indent + "│   "))

        return "\n".join(result)

    def __repr__(self) -> str:
        return f"Folder(path={self.path}, name={self.name}, files={len(self.files)}, subfolders={len(self.subfolders)})"


def create_folder_structure(path: str) -> Optional[Folder]:
    """
    Creates a Folder object representing the directory structure at the given path.

    Args:
        path: String path to the directory to create structure from

    Returns:
        Folder object representing the directory structure, or None if path doesn't exist
    """
    # Check if path exists
    if not os.path.exists(path):
        return None

    # Get the base folder name and create root Folder object
    # Normalize the path to handle both forward and backward slashes
    normalized_path = os.path.normpath(path)
    folder_name = os.path.basename(normalized_path)
    if folder_name == "":  # Handle root directory case
        folder_name = normalized_path

    # If path ends with a slash, take the last non-empty part
    if folder_name == "":
        parts = [p for p in normalized_path.split(os.sep) if p]
        folder_name = parts[-1] if parts else normalized_path

    root_folder = Folder(path=path, name=folder_name)

    try:
        # Iterate through directory contents
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    # Create and add File object
                    file_obj = File(path=entry.path, name=entry.name)
                    root_folder.add_file(file_obj)
                elif entry.is_dir():
                    # Recursively create and add subfolder
                    subfolder = create_folder_structure(entry.path)
                    if subfolder:
                        root_folder.add_subfolder(subfolder)

        return root_folder

    except PermissionError:
        print(f"Permission denied accessing {path}")
        return None
    except Exception as e:
        print(f"Error processing {path}: {str(e)}")
        return None
