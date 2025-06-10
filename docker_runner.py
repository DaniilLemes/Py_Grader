import tempfile
from pathlib import Path
from typing import Dict, Any

import docker


class DockerTaskRunner:
    """Utility class to run Python code inside a restricted Docker container."""

    def __init__(self,
                 image: str = "python:3.10-slim",
                 cpu_limit: float = 0.5,
                 mem_limit: str = "512m",
                 pids_limit: int = 64):
        self.image = image
        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.pids_limit = pids_limit
        self.client = docker.from_env()

    def run_code(self, code: str, timeout: int = 5) -> Dict[str, Any]:
        """Run the provided Python code inside the container and return execution info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            code_path = Path(tmpdir) / "main.py"
            code_path.write_text(code)

            container = self.client.containers.run(
                self.image,
                command=["python", str(code_path.name)],
                network_mode="none",
                detach=True,
                volumes={tmpdir: {"bind": "/code", "mode": "ro"}},
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
