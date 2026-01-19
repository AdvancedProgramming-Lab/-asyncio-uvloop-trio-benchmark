import trio
import httpx
import time

URL = "http://127.0.0.1:8000/test"
CONCURRENT_REQUESTS = 100

async def fetch(client, results):
    start = time.perf_counter()
    try:
        await client.get(URL)
        results.append(time.perf_counter() - start)
    except Exception:
        pass

async def run_benchmark():
    results = []
    async with httpx.AsyncClient() as client:
        start_time = time.perf_counter()
        
        # Trio usa nurseries para gerir o tempo de vida das tarefas
        async with trio.open_nursery() as nursery:
            for _ in range(CONCURRENT_REQUESTS):
                nursery.start_soon(fetch, client, results)
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        print(f"--- Trio ---")
        print(f"Total time: {total_time:.4f}s")
        print(f"Throughput: {len(results)/total_time:.2f} req/s")
        print(f"Avg Latency: {sum(results)/len(results):.4f}s\n")

if __name__ == "__main__":
    trio.run(run_benchmark)