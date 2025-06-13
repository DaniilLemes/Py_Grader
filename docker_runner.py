import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any

try:
    import docker  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    docker = None


class DockerTaskRunner:
    """Utility class to run Python code inside a restricted Docker container.

    If the Docker Python library or the ``docker`` executable is not available,
    the code will be executed directly on the host as a fallback. This keeps the
    rest of the application working even in minimal environments.
    """

    def __init__(self,
                 image: str = "python:3.10-slim",
                 cpu_limit: float = 0.5,
                 mem_limit: str = "512m",
                 pids_limit: int = 64):
        self.image = image
        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.pids_limit = pids_limit
        self.use_docker = docker is not None
        if self.use_docker:
            try:
                self.client = docker.from_env()
            except Exception:
                self.use_docker = False

    def run_code(
        self,
        code: str | None = None,
        *,
        dir_path: str | Path | None = None,
        entry: str = "main.py",
        args: list[str] | None = None,
        timeout: int = 5,
    ) -> Dict[str, Any]:
        """Run the provided Python code inside the container and return execution info.

        Parameters
        ----------
        code: str | None
            Source code of ``main.py`` to execute. If ``dir_path`` is provided,
            this may be ``None``.
        dir_path: str | Path | None
            Directory containing a ``main.py`` (or ``entry``) file to execute.
        entry: str
            Entry point filename relative to ``dir_path`` when running from an
            extracted archive.
        args: list[str] | None, optional
            Arguments to pass to the script as ``sys.argv[1:]``.
        timeout: int, optional
            Maximum execution time in seconds.
        """
        if args is None:
            args = []

        if dir_path is None:
            # Write provided code into a temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                code_path = Path(tmpdir) / "main.py"
                if code is None:
                    raise ValueError("code must be provided when dir_path is None")
                code_path.write_text(code)
                workdir = tmpdir
                entry_path = code_path.name
                return self._execute(workdir, entry_path, args, timeout)
        else:
            workdir = Path(dir_path)
            if not workdir.is_dir():
                raise FileNotFoundError(f"Directory not found: {workdir}")
            return self._execute(str(workdir), entry, args, timeout)

    def _execute(self, workdir: str, entry: str, args: list[str], timeout: int) -> Dict[str, Any]:
        """Helper to execute ``entry`` inside ``workdir`` either in Docker or locally."""
        if self.use_docker:
            container = self.client.containers.run(
                self.image,
                command=["python", entry, *args],
                network_mode="none",
                detach=True,
                volumes={workdir: {"bind": "/code", "mode": "ro"}},
                working_dir="/code",
                mem_limit=self.mem_limit,
                cpu_period=100000,
                cpu_quota=int(self.cpu_limit * 100000),
                pids_limit=self.pids_limit,
                stdout=True,
                stderr=True,
            )
            try:
                result = container.wait(timeout=timeout)
                logs = container.logs(stdout=True, stderr=True).decode()
                stats = container.stats(stream=False)
            finally:
                container.remove(force=True)

            return {
                "status": result.get("StatusCode"),
                "output": logs,
                "stats": stats,
            }
        else:
            proc = subprocess.run(
                ["python", entry, *args],
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "status": proc.returncode,
                "output": proc.stdout + proc.stderr,
                "stats": None,
            }
