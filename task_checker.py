from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple, List, Dict, Any
import zipfile

from docker_runner import DockerTaskRunner


def extract_code_from_archive(archive_path: str | Path) -> str:
    """Extract main.py from the provided zip archive and return its contents."""
    path = Path(archive_path)
    if not path.is_file():
        raise FileNotFoundError(f"Archive not found: {path}")

    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if name.lower().endswith('main.py'):
                with zf.open(name) as f:
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
    ``(input_data, expected_output)`` pairs. The candidate solution is expected
    to expose a function named ``solve`` which will be called for each test
    case. The return value is a list with one entry per test describing the
    execution outcome.
    """

    if code is None and archive is None:
        raise ValueError("Either code or archive must be supplied")

    if code is None:
        code = extract_code_from_archive(archive)  # type: ignore[arg-type]

    if runner is None:
        runner = DockerTaskRunner()

    results: List[Dict[str, Any]] = []
    for inp, expected in tests:
        test_code = f"{code}\nprint(solve({inp}))\n"
        res = runner.run_code(test_code, timeout=timeout)
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
