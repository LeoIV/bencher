import os
import subprocess
import threading


class ServiceThread(threading.Thread):
    def __init__(
            self,
            service_dir: str
    ):
        threading.Thread.__init__(self)
        self.dir = service_dir

    def run(
            self
    ):
        try:
            os.chdir(self.dir)
            print(f"Starting service in directory {self.dir}")
            subprocess.check_call(["poetry", "run", "start-benchmark-service"], stdout=open('/tmp/bencher.log', 'a'))
        except subprocess.CalledProcessError as e:
            raise Exception(f"Service failed in directory {self.dir}") from e


if __name__ == '__main__':
    os.environ["POETRY_VIRTUALENVS_PATH"] = "/opt/virtualenvs"
    os.environ["POETRY_HOME"] = "/opt/poetry"
    os.environ["PATH"] = "/opt/poetry/bin:" + os.environ["PATH"]
    os.environ["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"

    threads = []
    for service_dir in os.listdir("/opt/bencher"):
        # check if dir and pyproject.toml exists
        if os.path.isdir(os.path.join("/opt/bencher", service_dir)) and os.path.isfile(
                os.path.join("/opt/bencher", service_dir, "pyproject.toml")
        ):
            thread = ServiceThread(os.path.join("/opt/bencher", service_dir))
            thread.start()
            threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
