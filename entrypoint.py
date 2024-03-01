import os
import threading
import subprocess


class ServiceThread(threading.Thread):
    def __init__(
            self,
            dir: str
    ):
        threading.Thread.__init__(self)
        self.dir = dir

    def run(
            self
    ):
        try:
            os.chdir(self.dir)
            subprocess.check_call(["poetry", "run", "start-benchmark-service"], stdout=open('/tmp/bencher.log', 'a'))
        except subprocess.CalledProcessError as e:
            raise Exception(f"Service failed in directory {self.dir}") from e


if __name__ == '__main__':
    os.environ["POETRY_VIRTUALENVS_PATH"] = "/opt/virtualenvs"
    os.environ["POETRY_HOME"] = "/opt/poetry"
    os.environ["PATH"] = "/opt/poetry/bin:" + os.environ["PATH"]
    os.environ["POETRY_VIRTUALENVS_IN_PROJECT"] = "true"

    threads = []
    for dir in os.listdir("/opt/bencher"):
        if os.path.isdir(os.path.join("/opt/bencher", dir)):
            thread = ServiceThread(os.path.join("/opt/bencher", dir))
            thread.start()
            threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
