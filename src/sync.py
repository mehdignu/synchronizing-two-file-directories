import hashlib
import os
import shutil
import sys
from pathlib import Path

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


def sync(source: Path, destination: Path):
    source_hashes = {}
    for folder, _, files in os.walk(source):
        for file_name in files:
            source_path = Path(folder) / file_name
            source_hash = hash_file(source_path)
            source_hashes[source_hash] = file_name

    seen = set()

    for folder, _, files in os.walk(destination):
        for file_name in files:
            destination_path = Path(folder) / file_name
            destination_hash = hash_file(destination_path)
            seen.add(destination_hash)

            if destination_hash not in source_hashes:
                destination_path.unlink()
            elif (
                destination_hash in source_hashes
                and source_hashes[destination_hash] != file_name
            ):
                shutil.move(
                    destination_path, Path(folder) / source_hashes[destination_hash]
                )

    for source_hash, file_name in source_hashes.items():
        if source_hash not in seen:
            shutil.copy(Path(source) / file_name, Path(destination) / file_name)


if __name__ == "__main__":
    sync(Path(sys.argv[1]), Path(sys.argv[2]))
