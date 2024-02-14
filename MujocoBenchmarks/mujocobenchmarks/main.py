import logging

import numpy as np
from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService

from mujocobenchmarks.functions import func_factories

func_factory_map = {
    'mujoco-ant'        : lambda
        _: func_factories["ant"].make_object(),
    'mujoco-hopper'     : lambda
        _: func_factories["hopper"].make_object(),
    'mujoco-walker'     : lambda
        _: func_factories["walker_2d"].make_object(),
    'mujoco-halfcheetah': lambda
        _: func_factories["half_cheetah"].make_object(),
    'mujoco-swimmer'    : lambda
        _: func_factories["swimmer"].make_object(),
    'mujoco-humanoid'   : lambda
        _: func_factories["humanoid"].make_object(),
}


class MujocoServiceServicer(GRCPService):

    def __init__(
            self
    ):
        super().__init__(port=50057, n_cores=1)

    def EvaluatePoint(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        assert request.benchmark in func_factory_map.keys(), "Invalid benchmark name"
        x = request.point.values
        x = np.array(x).reshape(-1)
        func_factory = func_factory_map[request.benchmark](None)
        result = EvaluationResult(
            value=func_factory(x)[0].squeeze(),
        )
        return result


def serve():
    logging.basicConfig()
    mujoco = MujocoServiceServicer()
    mujoco.serve()
