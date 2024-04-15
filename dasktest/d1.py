from dask.distributed import Client

if __name__ == "__main__":
    client = Client(processes=False)

    def inc(x):
        return x + 1

    def add (x, y):
        return x + y

    a = client.submit(inc, 10)
    b = client.submit(inc, 30)
    c = client.submit(add, a, b)

    results = client.gather(futures=[a, b, c])
    print(results)