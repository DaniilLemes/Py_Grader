from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple, List, Dict, Any
import zipfile
import shlex

from docker_runner import DockerTaskRunner


def extract_code_from_archive(archive_path: str | Path) -> str:
    """Extract ``main.py`` from the provided zip archive.

    If ``main.py`` is not present but there is exactly one ``.py`` file in the
    archive, that file will be used as ``main.py``. This makes uploads a little
    more forgiving for users who forget to name their entry point correctly.
    """
    path = Path(archive_path)
    if not path.is_file():
        raise FileNotFoundError(f"Archive not found: {path}")

    with zipfile.ZipFile(path) as zf:
        py_files = [n for n in zf.namelist() if n.lower().endswith('.py')]
        for name in py_files:
            if name.lower().endswith('main.py'):
                with zf.open(name) as f:
                    return f.read().decode('utf-8')

        # Fallback: single python file becomes main
        if len(py_files) == 1:
            with zf.open(py_files[0]) as f:
                return f.read().decode('utf-8')

    raise FileNotFoundError("main.py not found in archive")


def check_solution(
    tests: Iterable[Tuple[str, str]],
    *,
    code: str | None = None,
    archive: str | Path | None = None,
    runner: DockerTaskRunner | None = None,
    timeout: int = 5,
) -> List[Dict[str, Any]]:
    """Run solution code against test cases using DockerTaskRunner.

    Either ``code`` or ``archive`` must be provided. ``tests`` is an iterable of
    ``(args, expected_output)`` pairs. Each ``args`` value is a string that will
    be parsed similar to a shell command and passed to ``main.py`` as
    ``sys.argv[1:]``. The return value contains one entry per test describing
    the execution outcome.
    """

    if code is None and archive is None:
        raise ValueError("Either code or archive must be supplied")

    if code is None:
        code = extract_code_from_archive(archive)  # type: ignore[arg-type]

    if runner is None:
        runner = DockerTaskRunner()

    results: List[Dict[str, Any]] = []
    for inp, expected in tests:
        argv = shlex.split(inp)
        res = runner.run_code(code, args=argv, timeout=timeout)
        output = res.get('output', '').strip()
        passed = output == str(expected)
        results.append({
            'input': inp,
            'expected': expected,
            'output': output,
            'passed': passed,
            'status': res.get('status'),
        })

    return results
