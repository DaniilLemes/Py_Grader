from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple, List, Dict, Any
import zipfile
import shlex

from docker_runner import DockerTaskRunner


def extract_code_from_archive(archive_path: str | Path) -> str:
    """Return the code for the entry point in the provided zip archive."""
    path = Path(archive_path)
    if not path.is_file():
        raise FileNotFoundError(f"Archive not found: {path}")

    with zipfile.ZipFile(path) as zf:
        py_files = [n for n in zf.namelist() if n.lower().endswith('.py')]
        main_file = next((n for n in py_files if Path(n).name.lower() == 'main.py'), None)
        if not main_file:
            if len(py_files) == 1:
                main_file = py_files[0]
            else:
                raise FileNotFoundError("main.py not found in archive")
        with zf.open(main_file) as f:
            return f.read().decode('utf-8')


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
    ``(input_data, expected_output)`` pairs. Each ``input_data`` string is
    treated as command line arguments which are supplied to ``main.py`` inside
    the Docker container. The return value is a list with one entry per test
    describing the execution outcome.
    """

    if code is None and archive is None:
        raise ValueError("Either code or archive must be supplied")

    if code is None:
        code = extract_code_from_archive(archive)  # type: ignore[arg-type]

    if runner is None:
        runner = DockerTaskRunner()

    results: List[Dict[str, Any]] = []
    for inp, expected in tests:
        args = shlex.split(inp)
        res = runner.run_code(code, args=args, timeout=timeout)
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
