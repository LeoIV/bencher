import logging

import LassoBench
import numpy as np
from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService


def eval_lasso(
        x: np.ndarray,
        benchmark
):
    return benchmark.evaluate(x)


benchmark_map = {
    'lasso-dna'   : lambda
        _: LassoBench.RealBenchmark(pick_data='dna', mf_opt='discrete_fidelity'),
    'lasso-simple': lambda
        _: LassoBench.SyntheticBenchmark(pick_bench='synt_simple'),
    'lasso-medium': lambda
        _: LassoBench.SyntheticBenchmark(pick_bench='synt_medium'),
    'lasso-high'  : lambda
        _: LassoBench.SyntheticBenchmark(pick_bench='synt_high'),
    'lasso-hard'  : lambda
        _: LassoBench.SyntheticBenchmark(pick_bench='synt_hard'),
    'lasso-leukemia': lambda
        _: LassoBench.RealBenchmark(pick_data='leukemia', mf_opt='discrete_fidelity'),
    'lasso-rcv1': lambda
        _: LassoBench.RealBenchmark(pick_data='rcv1', mf_opt='discrete_fidelity'),
    'lasso-diabetes': lambda
        _: LassoBench.RealBenchmark(pick_data='diabetes', mf_opt='discrete_fidelity'),
    'lasso-breastcancer': lambda
        _: LassoBench.RealBenchmark(pick_data='breast_cancer', mf_opt='discrete_fidelity'),
}


class LassoServiceServicer(GRCPService):

    def __init__(
            self
    ):
        super().__init__(port=50053, n_cores=1)

    def EvaluatePoint(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        assert request.benchmark in benchmark_map.keys(), "Invalid benchmark name"
        x = request.point.values
        x = np.array(x)
        benchmark = benchmark_map[request.benchmark](None)
        result = EvaluationResult(
            value=eval_lasso(x, benchmark),
        )
        return result


def serve():
    logging.basicConfig()
    lasso = LassoServiceServicer()
    lasso.serve()
