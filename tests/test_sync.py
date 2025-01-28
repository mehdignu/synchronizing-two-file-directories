import shutil
import tempfile
import unittest
from pathlib import Path

from src.sync import sync


class TestSync(unittest.TestCase):
    def test_when_a_file_exists_in_the_source_but_not_the_destination(self):
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a very useful file"
            (Path(source) / "my-file").write_text(content)

            sync(Path(source), Path(dest))

            expected_path = Path(dest) / "my-file"
            assert expected_path.exists()
            assert expected_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)

    def test_when_a_file_has_been_renamed_in_the_source(self):
        try:
            source = tempfile.mkdtemp()
            dest = tempfile.mkdtemp()

            content = "I am a file that was renamed"
            source_path = Path(source) / "source-filename"
            old_dest_path = Path(dest) / "dest-filename"
            expected_dest_path = Path(dest) / "source-filename"
            source_path.write_text(content)
            old_dest_path.write_text(content)

            sync(Path(source), Path(dest))

            assert old_dest_path.exists() is False
            assert expected_dest_path.read_text() == content

        finally:
            shutil.rmtree(source)
            shutil.rmtree(dest)
