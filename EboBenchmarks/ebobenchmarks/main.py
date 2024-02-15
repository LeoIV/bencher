import logging

import numpy as np
from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService
from ebo.test_functions.push_function import PushReward
from ebo.test_functions.rover_function import create_large_domain
from ebo.test_functions.rover_utils import RoverDomain


def eval_lasso(
        x: np.ndarray,
        benchmark
):
    return benchmark.evaluate(x)


class EboServiceServicer(GRCPService):

    def __init__(
            self
    ):
        super().__init__(port=50056, n_cores=1)
        self._pr = PushReward()

        def l2cost(
                x,
                point
        ):
            return 10 * np.linalg.norm(x - point, 1)

        domain: RoverDomain = create_large_domain(
            force_start=False,
            force_goal=False,
            start_miss_cost=l2cost,
            goal_miss_cost=l2cost,
        )
        self._domain = domain

    def EvaluatePoint(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        assert request.benchmark in ['robotpushing', 'rover'], "Invalid benchmark name"
        x = request.point.values
        x = np.array(x).squeeze()

        if request.benchmark == 'robotpushing':
            lb = np.array(self._pr.xmin)
            ub = np.array(self._pr.xmax)
            # x is in [0, 1] space, so we need to scale it to the domain
            x = lb + (ub - lb) * x
            assert x.shape[0] == 14, "Invalid input shape"
            rewards = -self._pr(x)
        else:
            # bounds are [0, 1] for the rover, so we don't need to scale
            assert x.shape[0] == 60, "Invalid input shape"
            rewards = -self._domain(x)
        result = EvaluationResult(
            value=rewards
        )
        return result


def serve():
    logging.basicConfig()
    ebo = EboServiceServicer()
    ebo.serve()
