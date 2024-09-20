import os
import subprocess
import sys
from pathlib import Path

import pytest


def get_example_scripts():
    return [
        pytest.param(fp, id=fp.name)
        for fp in Path(__file__).parents[1].glob("example/**/*.py")
    ]


@pytest.mark.parametrize(
    "fp",
    get_example_scripts(),
)
def test_example(fp: Path):
    env = os.environ.copy()
    env["CI"] = "true"
    ret = subprocess.run(
        [sys.executable, fp.absolute()],
        env=env,
    )
    assert ret.returncode == 0
