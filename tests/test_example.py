import os
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

_patch = """\
import matplotlib.pyplot as plt
def _show(*args, **kwargs):
    ...
plt.show = _show

"""


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
    env["MPLBACKEND"] = "agg"
    with NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        # python >= 3.12
        # with TemporaryFile("w", suffix=".py", delete_on_close=False) as tmp:
        tmp.write(_patch + fp.read_text(encoding="utf-8"))
        tmp.close()
        ret = subprocess.run(
            [sys.executable, tmp.name],
            env=env,
        )
        os.unlink(tmp.name)
    assert ret.returncode == 0
