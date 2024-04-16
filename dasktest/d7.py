from dask.distributed import Client

from snakeden._benchmark import _benchmark, get_all_benchmarks, BenchmarkSet

# LINK: https://docs.dask.org/en/latest/deploying-cli.html

def main():
    client = Client('100.93.155.38:9876')

    commit = '6e0b327690c7dd2e4e9091f81f8ad43ad5eb1631'
    pgo = False
    tier2 = False
    jit = False
    benchmarks = None
    #benchmarks = ['2to3', 'async_tree', 'float']
    benchmarks = ["concurrent_imap", "coroutines", "coverage"]

    if benchmarks == None:
        _benchmark_set = get_all_benchmarks()
    else:
        _benchmark_set = BenchmarkSet.fromList(benchmarks)

    futures = []
    for bm in _benchmark_set:
        futures.append(client.submit(_benchmark, 
            commit=commit,
            benchmarks=bm,
            pgo=pgo,
            tier2=tier2,
            jit=jit,
            jsonify=False,
            resources={'CPU':1}
        ))

    print(futures)

    print("THE RESULT IS: " + '\n---------\n'.join(client.gather(futures)))

if __name__ == "__main__":
    main()