import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from platform import machine

from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService
import numpy as np


class Mopta08ServiceServicer(GRCPService):

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
        assert request.benchmark == 'mopta08'
        x = request.point.values
        x = np.array(x)
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
    lasso = Mopta08ServiceServicer()
    lasso.serve()
