from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple, List, Dict, Any
import zipfile
import shlex


def _parse_args(inp: str) -> list[str]:
    """Parse the stored input string into ``sys.argv`` style arguments.

    The default behaviour uses ``shlex.split`` which splits on spaces.
    However many tasks store complex values such as ``"[1, 2, 3]"`` that
    should be passed as a single argument.  If the input string looks like
    a Python literal wrapped in brackets we treat it as one argument.
    """

    stripped = inp.strip()
    if stripped and stripped[0] in "[{(" and stripped[-1] in "]})":
        return [inp]
    return shlex.split(inp)

from docker_runner import DockerTaskRunner
from contextlib import contextmanager
import tempfile


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


@contextmanager
def extract_project_from_archive(archive_path: str | Path) -> tuple[Path, str]:
    """Extract a zip archive into a temporary directory and locate the entry file.

    Returns a tuple of ``(directory_path, entry_name)`` where ``entry_name`` is
    the relative path to ``main.py`` (or single ``.py`` file) inside the
    extracted directory. The temporary directory is cleaned up automatically when
    the context exits.
    """
    path = Path(archive_path)
    if not path.is_file():
        raise FileNotFoundError(f"Archive not found: {path}")

    tmpdir = tempfile.TemporaryDirectory()
    try:
        with zipfile.ZipFile(path) as zf:
            zf.extractall(tmpdir.name)
        root = Path(tmpdir.name)
        py_files = list(root.rglob("*.py"))
        entry = None
        for p in py_files:
            if p.name.lower() == "main.py":
                entry = p.relative_to(root)
                break
        if entry is None:
            if len(py_files) == 1:
                entry = py_files[0].relative_to(root)
            else:
                raise FileNotFoundError("main.py not found in archive")
        yield root, str(entry)
    finally:
        tmpdir.cleanup()


def check_solution(
    tests: Iterable[Tuple[str, str]],
    *,
    code: str | None = None,
    archive: str | Path | None = None,
    runner: DockerTaskRunner | None = None,
    timeout: int = 5,
) -> tuple[List[Dict[str, Any]], int]:
    """Run solution code against test cases using ``DockerTaskRunner``.

    Either ``code`` or ``archive`` must be provided. ``tests`` is an iterable of
    ``(args, expected_output)`` pairs. Each ``args`` value is a string that will
    be parsed similar to a shell command and passed to ``main.py`` as
    ``sys.argv[1:]``. The return value contains one entry per test describing
    the execution outcome.
    """

    if code is None and archive is None:
        raise ValueError("Either code or archive must be supplied")

    if runner is None:
        runner = DockerTaskRunner()

    results: List[Dict[str, Any]] = []
    passed_count = 0

    if code is None:
        with extract_project_from_archive(archive) as (dir_path, entry):
            for inp, expected in tests:
                argv = _parse_args(inp)
                res = runner.run_code(None, dir_path=dir_path, entry=entry, args=argv, timeout=timeout)
                output = res.get('output', '').strip()
                passed = output == str(expected)
                if passed:
                    passed_count += 1
                results.append({
                    'input': inp,
                    'expected': expected,
                    'output': output,
                    'passed': passed,
                    'status': res.get('status'),
                })
    else:
        for inp, expected in tests:
            argv = _parse_args(inp)
            res = runner.run_code(code, args=argv, timeout=timeout)
            output = res.get('output', '').strip()
            passed = output == str(expected)
            if passed:
                passed_count += 1
            results.append({
                'input': inp,
                'expected': expected,
                'output': output,
                'passed': passed,
                'status': res.get('status'),
            })

    return results, passed_count
