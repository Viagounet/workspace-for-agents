from typing import Self


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
            is_last = (i == len(self.subfolders) - 1)
            if is_last:
                result.append(subfolder.tree(indent + "    "))
            else:
                result.append(subfolder.tree(indent + "│   "))
                
        return "\n".join(result)

    def __repr__(self) -> str:
        return f"Folder(path={self.path}, name={self.name}, files={len(self.files)}, subfolders={len(self.subfolders)})"
