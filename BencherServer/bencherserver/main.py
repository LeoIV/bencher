from argparse import ArgumentParser

import os
from concurrent.futures import ThreadPoolExecutor

import grpc
from bencherscaffold import bencher_pb2_grpc

from bencherserver import BencherServer


def serve():
    argparse = ArgumentParser()
    argparse.add_argument(
        '-p',
        '--port',
        type=int,
        required=False,
        help='The port number to start the server on. Default is 50051.',
        default=50051
    )
    argparse.add_argument(
        '-c',
        '--cores',
        type=int,
        required=False,
        help='The number of CPU cores to use. If None, it will use the maximum number of CPU cores available on the system. Default is cpu_count()',
        default=os.cpu_count()
    )
    args = argparse.parse_args()

    bencher_server = BencherServer()
    bencher_server.register_stub(
        [
            'lasso-dna',
            'lasso-simple',
            'lasso-medium',
            'lasso-high',
            'lasso-hard'
            'lasso-leukemia',
            'lasso-rcv1',
            'lasso-diabetes',
            'lasso-breastcancer'
        ], 50053
    )

    bencher_server.register_stub(
        [
            'mopta08'
        ], 50054
    )

    bencher_server.register_stub(
        [
            'maxsat60',
            'maxsat125'
        ], 50055
    )

    bencher_server.register_stub(
        [
            'robotpushing',
            'rover'
        ], 50056
    )

    bencher_server.register_stub(
        [
            'mujo-ant',
            'mujoco-hopper',
            'mujoco-walker',
            'mujoco-halfcheetah',
            'mujoco-swimmer',
            'mujoco-humanoid'
        ], 50057
    )

    port = str(args.port)
    n_cores = args.cores
    server = grpc.server(ThreadPoolExecutor(max_workers=n_cores))
    bencher_pb2_grpc.add_BencherServicer_to_server(bencher_server, server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
