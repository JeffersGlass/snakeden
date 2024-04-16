import argparse

from ._benchmark import _benchmark, get_all_benchmarks, BenchmarkSet

from dask.distributed import Client, LocalCluster

benchmark = _benchmark

__all__ = [benchmark]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--benchmarks", help="A comma-separated list of benchmarks to run")
    parser.add_argument(
        "--commit", type=str, help="The commit to establish measure performance of", required=True)
    parser.add_argument(
        "--fork", default="python/cpython", help="The fork of CPython the commit lives on")
    parser.add_argument(
        "--address", help="The address and port of the Dask server to run on. If left blank, will run on local client with n_workers = 2."
        )
    parser.add_argument(
        "--pgo", action="store_true", help="Enable the pgo flag")
    parser.add_argument(
        "--tier2", action="store_true", help="Enable the tier2 flag")
    parser.add_argument(
        "--jit", action="store_true", help="Enable the jit flag")
    
    args = parser.parse_args()
    print(f"{args.benchmarks=}")

    if args.address == None:
        client = LocalCluster().get_client()
    else:
        #client = Client('100.93.155.38:9876')
        client = Client(args.address)

    commit = args.commit
    pgo = args.pgo
    tier2 = args.tier2
    jit = args.jit

    if args.benchmarks == None:
        _benchmark_set = get_all_benchmarks()
    else:
        _benchmark_set = BenchmarkSet.fromString(args.benchmarks)

    #benchmarks = ['2to3', 'async_tree', 'float']
    #benchmarks = ["concurrent_imap", "coroutines", "coverage"]

    futures = []
    for bm in _benchmark_set:
        print(f"Assigning {bm=}")
        futures.append(client.submit(_benchmark, 
            commit=commit,
            benchmarks=bm,
            pgo=pgo,
            tier2=tier2,
            jit=jit,
            jsonify=False,
            resources={'CPU':1}
        ))