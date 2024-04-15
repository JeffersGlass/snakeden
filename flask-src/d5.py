from dask.distributed import Client

from _benchmark import _benchmark

# LINK: https://docs.dask.org/en/latest/deploying-cli.html

def main():
    client = Client('172.16.49.180:8786')

    commit = '9ee94d139197c0df8f4e096957576d124ad31c8e'
    pgo = False
    tier2 = False
    jit = False

    futures = []
    #for bm in bench_list:
    futures.append(client.submit(_benchmark, 
        commit=commit,
        benchmarks='2to3',
        pgo=pgo,
        tier2=tier2,
        jit=jit,
        jsonify=False
    ))

    futures.append(client.submit(_benchmark, 
        commit=commit,
        benchmarks='async_tree',
        pgo=pgo,
        tier2=tier2,
        jit=jit,
        jsonify=False
    ))

    futures.append(client.submit(_benchmark, 
        commit=commit,
        benchmarks='float',
        pgo=pgo,
        tier2=tier2,
        jit=jit,
        jsonify=False
    ))

    print(futures)

    print("THE RESULT IS: " + '\n---------\n'.join(client.gather(futures)))

if __name__ == "__main__":
    main()