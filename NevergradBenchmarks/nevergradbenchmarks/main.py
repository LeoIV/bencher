import logging

import numpy as np
from bencherscaffold.protoclasses.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.protoclasses.grcp_service import GRCPService
from nevergrad.benchmark.experiments import complex_tsp


class NevergradServiceServicer(GRCPService):

    def __init__(
            self
    ):
        super().__init__(port=50060, n_cores=1)

    def evaluate_point(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        x = request.point.values
        x = np.array(x)
        dimension = x.shape[0]

        y = x #benchmark(x.astype(point_type))
        result = EvaluationResult(
            value=y,
        )
        return result


def serve():
    logging.basicConfig()
    nvg = NevergradServiceServicer()
    nvg.serve()


if __name__ == '__main__':
    serve()
