from functools import partial

from dask.distributed import LocalCluster

from _benchmark import _benchmark

if __name__ == "__main__":
        cluster = LocalCluster(n_workers=2)
        client = cluster.get_client()

        bench_list = ['2to3', 'async_tree']
        
        commit = '784e076a10e828f383282df8a4b993a1b821f547'
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

        a = client.submit(_benchmark, 
            commit=commit,
            benchmarks='async_tree',
            pgo=pgo,
            tier2=tier2,
            jit=jit,
            jsonify=False
        )
        futures.append(a)
        print(futures)

        print("THE RESULT IS: " + '\n---------\n'.join(client.gather(futures)))