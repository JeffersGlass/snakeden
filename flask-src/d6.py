from dask.distributed import Client

from _benchmark import _benchmark, get_all_benchmarks, BenchmarkSet

# LINK: https://docs.dask.org/en/latest/deploying-cli.html

def main():
    client = Client('172.16.49.180:8786')

    commit = '3375282bb894347b73c11752f0797d90dadaf465'
    pgo = False
    tier2 = False
    jit = False
    benchmarks = None
    benchmarks = ['2to3', 'async_tree', 'float']

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