import asyncio
import time
import httpx

URL = "http://127.0.0.1:8000/test"
TOTAL_REQUESTS = 5000
CONCURRENCY_LIMIT = 100  # Máximo de pedidos ao mesmo tempo

async def fetch(client, semaphore):
    async with semaphore:
        start = time.perf_counter()
        try:
            await client.get(URL)
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
        
        latencies = [l for l in latencies if l is not None]
        total_time = end_overall - start_overall
        
        print(f"--- Asyncio Standard ---")
        print(f"Total Requests: {len(latencies)}")
        print(f"Total time: {total_time:.4f}s")
        print(f"Throughput: {len(latencies)/total_time:.2f} req/s")
        print(f"Avg Latency: {sum(latencies)/len(latencies):.4f}s\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())