"""When the kit is cloned into a project as kit/, the project's `pytest` must not collect the kit's
own tests (they need files a practice run removes). They still run from the kit's own folder."""

from pathlib import Path

KIT = Path(__file__).parent


def pytest_ignore_collect(collection_path, config):
    return config.rootpath != KIT
