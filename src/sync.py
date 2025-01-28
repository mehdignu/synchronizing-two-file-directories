import hashlib
import os
import shutil
import sys
from pathlib import Path
from typing import Dict

BLOCKSIZE = 65536


def hash_file(path: Path) -> str:
    """Hash a file and return its hash."""
    hasher = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCKSIZE)
        while buf:
            hasher.update(buf)
            buf = file.read(BLOCKSIZE)
    return hasher.hexdigest()


def read_paths_and_hashes(path: Path) -> Dict[str, str]:
    result_hashes: Dict[str, str] = {}
    for folder, _, files in os.walk(path):
        for file_name in files:
            current_path = Path(folder) / file_name
            current_hash = hash_file(current_path)
            result_hashes[current_hash] = file_name
    return result_hashes


def determine_actions(source_hashes, dest_hashes, source_folder, dest_folder):
    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            source_path = Path(source_folder) / filename
            dest_path = Path(dest_folder) / filename
            yield "COPY", source_path, dest_path

        elif dest_hashes[sha] != filename:
            olddest_path = Path(dest_folder) / dest_hashes[sha]
            newdest_path = Path(dest_folder) / filename
            yield "MOVE", olddest_path, newdest_path

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            yield "DELETE", dest_folder / filename


def sync(source: Path, destination: Path):
    # gather inputs
    source_hashes = read_paths_and_hashes(source)
    destination_hashes = read_paths_and_hashes(destination)

    # call functional core
    actions = determine_actions(source_hashes, destination_hashes, source, destination)

    # apply outputs
    for action, *paths in actions:
        if action == "COPY":
            shutil.copyfile(*paths)
        if action == "MOVE":
            shutil.move(*paths)
        if action == "DELETE":
            os.remove(paths[0])


if __name__ == "__main__":
    sync(Path(sys.argv[1]), Path(sys.argv[2]))
