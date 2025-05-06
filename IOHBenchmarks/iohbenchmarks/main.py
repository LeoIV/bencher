import logging

import ioh.iohcpp
import numpy as np
from bencherscaffold.protoclasses.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.protoclasses.grcp_service import GRCPService
from ioh import get_problem


class IOHServiceServicer(GRCPService):

    def __init__(
            self
    ):
        super().__init__(port=50059, n_cores=1)

    def evaluate_point(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        x = request.point.values
        x = np.array(x)
        dimension = x.shape[0]
        if request.benchmark.name.strip().startswith('bbob'):
            print(f"Evaluating {request.benchmark.name} with dimension {dimension}")
            bname_trunc = request.benchmark.name.split('-')[1]
            benchmark_candidate = ioh.iohcpp.problem.BBOB.problems

            pname, pid = [
                (name, pid) for pid, name in benchmark_candidate.items() if name.lower().startswith(bname_trunc)
            ][0]
            benchmark = get_problem(pname, pid, dimension)
            bounds = benchmark.bounds
            if bounds is not None:
                x = (x - bounds.lb) / (bounds.ub - bounds.lb)
            y = benchmark(x)
        else:
            raise ValueError(
                f"Benchmark {request.benchmark.name} not supported. Supported benchmarks are: {list(ioh.iohcpp.problem.BBOB.problems.values())}"
            )
        result = EvaluationResult(
            value=y,
        )
        return result


def serve():
    logging.basicConfig()
    ioh = IOHServiceServicer()
    ioh.serve()
