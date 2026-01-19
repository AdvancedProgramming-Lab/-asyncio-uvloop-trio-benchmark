import curio
import httpx
import time

URLS = ["http://localhost:1880" for _ in range(1)]

async def fetch(client, url):
    try:
        resp = await client.get(url, timeout=10.0)
        return {"url": url, "status": resp.status_code, "error": None}
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {"url": url, "status": None, "error": str(e)}

async def fetch_and_store(client, url, results):
    result = await fetch(client, url)
    results.append(result)

async def bench_w_session_creation():
    total_start = time.perf_counter()

    for _ in range(5):
        start = time.perf_counter()
        results = []
        
        async with httpx.AsyncClient() as client:
            async with curio.TaskGroup() as g:
                for url in URLS:
                    await g.spawn(fetch_and_store, client, url, results)

        successful = [r for r in results if r["status"] == 200]
        end = time.perf_counter()

        print(f"curio: fetched {len(URLS)} URLs in {end - start:.4f} seconds (successful: {len(successful)}/{len(URLS)})")

        await curio.sleep(1)

    total_end = time.perf_counter()
    print(f"curio: total busy time: {total_end - total_start - 5:.4f} seconds")

async def bench_w_connection_pool_reuse():
    total_start = time.perf_counter()

    async with httpx.AsyncClient() as client:
        for _ in range(5):
            start = time.perf_counter()
            results = []
            
            async with curio.TaskGroup() as g:
                for url in URLS:
                    await g.spawn(fetch_and_store, client, url, results)

            successful = [r for r in results if r["status"] == 200]
            end = time.perf_counter()

            print(f"curio: fetched {len(URLS)} URLs in {end - start:.4f} seconds (successful: {len(successful)}/{len(URLS)})")

            await curio.sleep(1)

    total_end = time.perf_counter()
    print(f"curio: total busy time: {total_end - total_start - 5:.4f} seconds")

if __name__ == "__main__":
    print("=" * 50)
    print("curio bench with NEW session per iteration")
    curio.run(bench_w_session_creation)

    print("=" * 50)
    print("curio bench with SINGLE session reuse across iterations")
    curio.run(bench_w_connection_pool_reuse)
