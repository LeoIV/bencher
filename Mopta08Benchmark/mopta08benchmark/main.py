import logging
import numpy as np
import os
import subprocess
import sys
import tempfile
from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService
from pathlib import Path
from platform import machine


def download_mopta_executable(
        executable_name: str
):
    if not Path(__file__).parent.joinpath(executable_name).exists():
        logging.info(f"{executable_name} not found. Downloading...")
        url = f"http://mopta-executables.s3-website.eu-north-1.amazonaws.com/{executable_name}"
        logging.info(f"Downloading {url}")

        import requests
        response = requests.get(url, verify=False)

        with open(os.path.join(Path(__file__).parent, executable_name), "wb") as file:
            file.write(response.content)
        # make executable
        os.chmod(os.path.join(Path(__file__).parent, executable_name), 0o755)
        logging.info(f"Downloaded {executable_name}")


class Mopta08ServiceServicer(GRCPService):
    """
    Mopta08ServiceServicer

    This class is a gRPC service for evaluating points against the Mopta08 benchmark. It provides methods for evaluating points and returning the evaluation results.

    Attributes:
        sysarch (int): The system architecture (32 or 64) based on the maximum size. Default is 64.
        machine (str): The machine on which the service is running. Default is the lowercase machine name.
        _mopta_exectutable (str): The name of the mopta08 executable file based on the system architecture and machine.
                                  This will be used for evaluating points.
        directory_file_descriptor (TemporaryDirectory): A temporary directory object for storing input and output files.
        directory_name (str): The name of the temporary directory.

    Methods:
        __init__():
            Initializes the Mopta08ServiceServicer object with the gRPC service port and number of cores.
            Sets the sysarch attribute based on the system's maximum size.
            Sets the machine attribute based on the lowercase machine name.
            Sets the _mopta_exectutable attribute based on the machine and sysarch.
            Downloads the mopta executable file if it does not exist.
            Sets the _mopta_exectutable attribute to the full path of the executable file.
            Creates a temporary directory for storing input and output files.

        EvaluatePoint(request: BenchmarkRequest, context) -> EvaluationResult:
            Evaluates the given point against the Mopta08 benchmark.
            :param request: The benchmark request object containing the point to evaluate.
            :type request: BenchmarkRequest
            :param context: The evaluation context.
            :type context: Any
            :return: The evaluation result.
            :rtype: EvaluationResult

        eval(x: np.ndarray) -> float:
            Evaluates the function with the given input.
            :param x: Input array.
            :type x: np.ndarray
            :return: The evaluated result.
            :rtype: float
    """
    def __init__(
            self
    ):
        super().__init__(port=50054, n_cores=1)

        self.sysarch = 64 if sys.maxsize > 2 ** 32 else 32
        self.machine = machine().lower()

        if self.machine == "armv7l":
            assert self.sysarch == 32, "Not supported"
            self._mopta_exectutable = "mopta08_armhf.bin"
        elif self.machine == "x86_64":
            assert self.sysarch == 64, "Not supported"
            self._mopta_exectutable = "mopta08_elf64.bin"
        elif self.machine == "i386":
            assert self.sysarch == 32, "Not supported"
            self._mopta_exectutable = "mopta08_elf32.bin"
        elif self.machine == "amd64":
            assert self.sysarch == 64, "Not supported"
            self._mopta_exectutable = "mopta08_amd64.exe"
        else:
            raise RuntimeError("Machine with this architecture is not supported")
        download_mopta_executable(self._mopta_exectutable)

        self._mopta_exectutable = os.path.join(
            Path(__file__).parent, self._mopta_exectutable
        )

        self.directory_file_descriptor = tempfile.TemporaryDirectory()
        self.directory_name = self.directory_file_descriptor.name

    def EvaluatePoint(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        """

        .. function:: EvaluatePoint(self, request: BenchmarkRequest, context) -> EvaluationResult

            Evaluate the given point against the specified benchmark.

            :param request: The benchmark request object containing the point to evaluate.
            :type request: BenchmarkRequest
            :param context: The evaluation context.
            :type context: Any
            :return: The evaluation result.
            :rtype: EvaluationResult

        """
        assert request.benchmark == 'mopta08'
        x = request.point.values
        x = np.array(x)
        # mopta is in [0, 1]^n so we don't need to scale
        result = EvaluationResult(
            value=self.eval(x)
        )
        return result

    def eval(
            self,
            x: np.ndarray
    ) -> float:
        """
        Evaluate the function with the given input.

        :param x: Input array.
        :type x: np.ndarray
        :return: The evaluated result.
        :rtype: float
        """
        x = x.squeeze()
        assert x.ndim == 1
        # write input to file in dir
        with open(os.path.join(self.directory_name, "input.txt"), "w+") as tmp_file:
            for _x in x:
                tmp_file.write(f"{_x}\n")
        # pass directory as working directory to process
        popen = subprocess.Popen(
            self._mopta_exectutable,
            stdout=subprocess.PIPE,
            cwd=self.directory_name,
        )
        popen.wait()
        # read and parse output file
        output = (
            open(os.path.join(self.directory_name, "output.txt"), "r")
            .read()
            .split("\n")
        )
        output = [x.strip() for x in output]
        output = np.array([float(x) for x in output if len(x) > 0])
        value = output[0]
        constraints = output[1:]
        # see https://arxiv.org/pdf/2103.00349.pdf E.7
        return float(value + 10 * np.sum(np.clip(constraints, a_min=0, a_max=None)))


def serve():
    logging.basicConfig()
    mopta = Mopta08ServiceServicer()
    mopta.serve()
