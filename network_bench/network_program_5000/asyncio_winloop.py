import asyncio
import winloop
import time
import httpx

URL = "http://127.0.0.1:8000/test"
TOTAL_REQUESTS = 5000
CONCURRENCY_LIMIT = 100

async def fetch(client, semaphore):
    async with semaphore:
        start = time.perf_counter()
        try:
            resp = await client.get(URL)
            return time.perf_counter() - start
        except Exception:
            return None

async def run_benchmark():
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    async with httpx.AsyncClient() as client:
        start_overall = time.perf_counter()
        
        tasks = [fetch(client, semaphore) for _ in range(TOTAL_REQUESTS)]
        latencies = await asyncio.gather(*tasks)
        
        end_overall = time.perf_counter()
        
        # Filtrar apenas pedidos com sucesso
        latencies = [l for l in latencies if l is not None]
        total_time = end_overall - start_overall
        
        print(f"--- Asyncio + Winloop ---")
        print(f"Total Requests: {len(latencies)}")
        print(f"Total time: {total_time:.4f}s")
        print(f"Throughput: {len(latencies)/total_time:.2f} req/s")
        if latencies:
            print(f"Avg Latency: {sum(latencies)/len(latencies):.4f}s")
        print("-" * 25)

if __name__ == "__main__":
    winloop.install()
    asyncio.run(run_benchmark())