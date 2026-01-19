import asyncio
import time
import httpx

URL = "http://127.0.0.1:8000/test"
CONCURRENT_REQUESTS = 5000

async def fetch(client):
    start = time.perf_counter()
    try:
        resp = await client.get(URL)
        latency = time.perf_counter() - start
        return latency
    except Exception:
        return None

async def run_benchmark():
    async with httpx.AsyncClient() as client:
        start_time = time.perf_counter()
        
        # Cria as tarefas
        tasks = [fetch(client) for _ in range(CONCURRENT_REQUESTS)]
        latencies = await asyncio.gather(*tasks)
        
        end_time = time.perf_counter()
        
        # Filtra falhas e calcula métricas
        latencies = [l for l in latencies if l is not None]
        total_time = end_time - start_time
        print(f"--- Asyncio Standard ---")
        print(f"Total time: {total_time:.4f}s")
        print(f"Throughput: {len(latencies)/total_time:.2f} req/s")
        print(f"Avg Latency: {sum(latencies)/len(latencies):.4f}s\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())