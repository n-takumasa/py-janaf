import contextlib
import os
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


def get_example_scripts():
    return [
        pytest.param(fp, id=fp.name)
        for fp in Path(__file__).parents[1].glob("example/**/*.py")
    ]


@pytest.mark.filterwarnings(
    "ignore:.*'mode' parameter is deprecated.*:DeprecationWarning:matplotlib.*"
)
@pytest.mark.parametrize("fp", get_example_scripts())
def test_example(fp: Path):
    with contextlib.ExitStack() as stack:
        with contextlib.suppress(ModuleNotFoundError):
            import matplotlib

            matplotlib.use("Agg", force=True)
            stack.enter_context(patch("matplotlib.pyplot.show"))

        try:
            runpy.run_path(str(fp), run_name="__main__")
        except ModuleNotFoundError as e:
            _truly = {"y", "yes", "t", "true", "on", "1"}
            if os.getenv("ALLOW_MISSING_DEPS", "").lower() in _truly:
                pytest.skip(e.msg)
            else:  # no cover
                raise

    if "matplotlib.pyplot" in sys.modules:
        sys.modules["matplotlib.pyplot"].close("all")
