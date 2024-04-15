from dask.distributed import Client

from _benchmark import _benchmark, get_all_benchmarks
from _runner import run_commands

# LINK: https://docs.dask.org/en/latest/deploying-cli.html

def main():
    client = Client('172.16.49.180:8786')

    commit = '9ee94d139197c0df8f4e096957576d124ad31c8e'
    pgo = False
    tier2 = False
    jit = False
    benchmarks = None

    if benchmarks == None:
        _benchmark_set = get_all_benchmarks()

    futures = []
    for bm in _benchmark_set:
        futures.append(client.submit(_benchmark, 
            commit=commit,
            benchmarks=bm,
            pgo=pgo,
            tier2=tier2,
            jit=jit,
            jsonify=False
        ))

    print(futures)

    print("THE RESULT IS: " + '\n---------\n'.join(client.gather(futures)))

if __name__ == "__main__":
    main()