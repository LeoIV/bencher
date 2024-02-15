import io
import logging
import lzma
import os
from pathlib import Path

import numpy as np
import requests
from bencherscaffold.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.grcp_service import GRCPService
from numpy.random import RandomState
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR


class SvmServiceServicer(GRCPService):

    def __init__(
            self
    ):
        super().__init__(port=50058, n_cores=1)
        self.X, self.y = self._load_data()
        idxs = RandomState(388).choice(np.arange(len(self.X)), min(10000, len(self.X)), replace=False)
        half = len(idxs) // 2
        self._X_train = self.X[idxs[:half]]
        self._X_test = self.X[idxs[half:]]
        self._y_train = self.y[idxs[:half]]
        self._y_test = self.y[idxs[half:]]

    def EvaluatePoint(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        assert request.benchmark == "svm", "Invalid benchmark name"
        x = request.point.values
        x = np.array(x).squeeze()
        C = 0.01 * (500 ** x[387])
        gamma = 0.1 * (30 ** x[386])
        epsilon = 0.01 * (100 ** x[385])
        length_scales = np.exp(4 * x[:385] - 2)

        svr = SVR(gamma=gamma, epsilon=epsilon, C=C, cache_size=1500, tol=0.001)
        svr.fit(self._X_train / length_scales, self._y_train)
        pred = svr.predict(self._X_test / length_scales)
        error = np.sqrt(np.mean(np.square(pred - self._y_test)))
        result = EvaluationResult(
            value=float(error)
        )
        return result

    def _load_data(
            self,
    ):
        self.download_slice_localization_data()
        data_folder = Path(__file__).parent
        if not os.path.exists(os.path.join(data_folder, "CT_slice_X.npy")):
            data = np.genfromtxt(
                os.path.join(data_folder, "slice_localization_data.csv"),
                delimiter=","
            )
            X = data[:, :385]
            y = data[:, -1]
            np.save(os.path.join(data_folder, "CT_slice_X.npy"), X)
            np.save(os.path.join(data_folder, "CT_slice_y.npy"), y)
        X = np.load(os.path.join(data_folder, "CT_slice_X.npy"))
        y = np.load(os.path.join(data_folder, "CT_slice_y.npy"))
        X = MinMaxScaler().fit_transform(X)
        y = MinMaxScaler().fit_transform(y.reshape(-1, 1)).squeeze()
        return X, y

    def download_slice_localization_data(
            self,
    ):
        if not os.path.exists(os.path.join(Path(__file__).parent, "slice_localization_data.csv")):
            url = "http://mopta-executables.s3-website.eu-north-1.amazonaws.com/slice_localization_data.csv.xz"
            response = requests.get(url)
            # unpack the data
            with lzma.open(io.BytesIO(response.content)) as f:
                with open(os.path.join(Path(__file__).parent, "slice_localization_data.csv"), "wb") as out:
                    out.write(f.read())


def serve():
    logging.basicConfig()
    lasso = SvmServiceServicer()
    lasso.serve()
