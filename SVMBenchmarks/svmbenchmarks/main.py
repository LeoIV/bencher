import io
import logging
import lzma
import os
import tempfile
import threading

import numpy as np
from bencherscaffold.protoclasses.bencher_pb2 import BenchmarkRequest, EvaluationResult
from bencherscaffold.protoclasses.grcp_service import GRCPService
from numpy.random import RandomState
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR

directory_file_descriptor = tempfile.TemporaryDirectory()
directory_name = directory_file_descriptor.name
lock = threading.Lock()


def download_slice_localization_data():
    """
    Downloads the slice localization data from a specified URL and saves it locally.

    :return: None
    """
    if not os.path.exists(os.path.join(directory_name, "slice_localization_data.csv")):
        print(f"{os.path.join(directory_name, 'slice_localization_data.csv')} not found. Downloading...")
        url = "http://mopta-executables.s3-website.eu-north-1.amazonaws.com/slice_localization_data.csv.xz"
        print(f"Downloading {url}")
        import requests
        response = requests.get(url, verify=False)

        # save the .xz file
        with open(os.path.join(directory_name, "slice_localization_data.csv.xz"), "wb") as out:
            out.write(response.content)
        # unpack the data
        with lzma.open(os.path.join(directory_name, "slice_localization_data.csv.xz"), "rb") as f, open(
                os.path.join(directory_name, "slice_localization_data.csv"), "wt"
        ) as out:
            out.write(f.read().decode("utf-8"))

        print(f"Downloaded slice_localization_data.csv")


def _load_data():
    """
    _load_data()
    -----------

    This method is used to load data for CT slice localization. It downloads the data if necessary and processes it for further use.

    :return: A tuple containing the features (X) and labels (y) of the CT data. X is a numpy array of shape (n_samples, n_features) and y is a numpy array of shape (n_samples,). The features
    * and labels are scaled using MinMaxScaler.

    Example usage:

        >>> X, y = _load_data()
    """

    download_slice_localization_data()
    if not os.path.exists(os.path.join(directory_name, "CT_slice_X.npy")):
        data = np.genfromtxt(
            os.path.join(directory_name, "slice_localization_data.csv"),
            delimiter=","
        )
        X = data[:, :385]
        y = data[:, -1]
        np.save(os.path.join(directory_name, "CT_slice_X.npy"), X)
        np.save(os.path.join(directory_name, "CT_slice_y.npy"), y)
    X = np.load(os.path.join(directory_name, "CT_slice_X.npy"))
    y = np.load(os.path.join(directory_name, "CT_slice_y.npy"))
    X = MinMaxScaler().fit_transform(X)
    y = MinMaxScaler().fit_transform(y.reshape(-1, 1)).squeeze()
    return X, y


class SvmServiceServicer(GRCPService):
    """
    This class is a GRCP service for SVM evaluation.

    Attributes:
        - X (numpy.ndarray): Input data for training.
        - y (numpy.ndarray): Target values for training.
        - _X_train (numpy.ndarray): Input data for training, subset of X.
        - _X_test (numpy.ndarray): Input data for testing, subset of X.
        - _y_train (numpy.ndarray): Target values for training, subset of y.
        - _y_test (numpy.ndarray): Target values for testing, subset of y.

    Methods:
        - __init__(self): Initializes the SVM service.
        - evaluate_point(self, request: BenchmarkRequest, context) -> EvaluationResult: Evaluates a point using SVM.

    """

    def __init__(
            self
    ):
        super().__init__(port=50058)
        self.data_initialized = False

    def initialize_data(
            self
    ):
        self.X, self.y = _load_data()
        idxs = RandomState(388).choice(np.arange(len(self.X)), min(500, len(self.X)), replace=False)
        half = len(idxs) // 2
        self._X_train = self.X[idxs[:half]]
        self._X_test = self.X[idxs[half:]]
        self._y_train = self.y[idxs[:half]]
        self._y_test = self.y[idxs[half:]]

    def evaluate_point(
            self,
            request: BenchmarkRequest,
            context
    ) -> EvaluationResult:
        """
        evaluate_point Method

        :param request: An instance of the BenchmarkRequest class, representing the request to evaluate a point.
        :param context: The context in which the evaluation is being performed.
        :return: An instance of the EvaluationResult class, representing the result of the evaluation.

        This method evaluates the given point using an SVM regression model. It first extracts the values from the request's point, and applies transformations to them to calculate the SVM model
        * parameters. It then fits the SVM regression model using the transformed training data and evaluates it against the transformed test data. The evaluation result, represented as the
        * root mean square error (RMSE), is returned as an instance of the EvaluationResult class.

        Please note that this method assumes that the benchmark name in the request is "svm". If the benchmark name is different, an assertion error will occur.
        """
        assert request.benchmark == "svm", "Invalid benchmark name"
        with lock:
            if not self.data_initialized:
                self.initialize_data()
                self.data_initialized = True

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


def serve():
    logging.basicConfig()
    svm = SvmServiceServicer()
    svm.serve()
