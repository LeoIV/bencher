from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService


class DNAServiceServicer(GRCPService):

    def eval_lasso(self, x: np.ndarray, benchmark):
        benchmark.evaluate(x.cpu().numpy().astype(np.double)

    def EvaluatePoint(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        print("Evaluating point")
        assert request.benchmark == "dna", "Invalid benchmark name"
        x = request.point.values
        result = EvaluationResult(
            value=sum(x),
        )

        return result
