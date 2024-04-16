#from dask.distributed import LocalCluster

from dask_kubernetes.operator import KubeCluster
# LINK: https://kubernetes.dask.org/en/latest/operator_kubecluster.html
# LINK: https://docs.dask.org/en/latest/deploying-kubernetes.html

from snakeden._benchmark import _benchmark

print("Hello?")

if __name__ == "__main__":
        cluster = KubeCluster(name='foo', image='ghcr.io/dask/dask:latest')
        cluster.scale(2)
        print(cluster.dashboard_link)
        client = cluster.get_client()

        bench_list = ['2to3', 'async_tree']
        
        commit = '185999bb3ad3f1484da8fa4b84813980b976dc3c'
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