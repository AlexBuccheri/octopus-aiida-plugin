import importlib.util
from pathlib import Path

import subprocess
import pytest

from aiida import orm
from aiida.common.exceptions import MultipleObjectsError, NotExistent

if importlib.util.find_spec("aiida.tools.pytest_fixtures") is not None:
    pytest_plugins = ("aiida.tools.pytest_fixtures",)
else:
    pytest_plugins = ("aiida.manage.tests.pytest_fixtures",)


@pytest.fixture(scope="session")
def octopus_executable() -> Path:
    """Check that ``octopus`` is present in the ``PATH`` and return its absolute path.

    :return: Absolute path to the executable.
    """
    try:
        result = subprocess.run(["which", "octopus"], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as err:
        message = err.stderr.strip() or err.stdout.strip() or "`octopus` is not present in the PATH."
        raise RuntimeError(message) from err

    return Path(result.stdout.strip())


@pytest.fixture
def aiida_create_or_load_code(aiida_profile_clean, aiida_localhost, octopus_executable: Path):
    """Return a helper that creates or loads a test code for a specific plugin.

    Providing aiida_profile_clean as an arg forces pytest to load it
    prior to running this fixture. This:
     * ensures an AiiDA profile is loaded
     * resets the storage before the test
    """

    def _create_or_load_code(code_label: str, calc_job_plugin: str):
        label = code_label.split('@', maxsplit=1)[0]
        builder = orm.QueryBuilder().append(
            orm.InstalledCode,
            filters={
                'label': label,
                'attributes.input_plugin': calc_job_plugin,
            },
        )

        try:
            code = builder.one()[0]
        except (NotExistent, MultipleObjectsError):
            code = orm.InstalledCode(
                label=label,
                computer=aiida_localhost,
                filepath_executable=octopus_executable.as_posix(),
                default_calc_job_plugin=calc_job_plugin
            ).store()

        return code

    return _create_or_load_code
