import asyncio
import aiohttp
import time

URLS = ["http://localhost:1337" for _ in range(50)]


async def fetch(session, url):
    try:
        async with session.get(url, timeout=10.0) as resp:
            return {"url": url, "status": resp.status, "error": None}
    except Exception as e:
        return {"url": url, "status": None, "error": str(e)}


async def fetch_and_store(session, url, results):
    result = await fetch(session, url)
    results.append(result)


async def bench_w_session_creation():
    total_start = time.perf_counter()

    for _ in range(5):
        start = time.perf_counter()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            results = []
            for url in URLS:
                task = asyncio.create_task(fetch_and_store(session, url, results))
                tasks.append(task)
            
            await asyncio.gather(*tasks)

        successful = [r for r in results if r["status"] == 200]

        end = time.perf_counter()

        print(f"asyncio: fetched {len(URLS)} URLs in {end - start:.4f} seconds (successful: {len(successful)}/{len(URLS)})")

        await asyncio.sleep(1)

    total_end = time.perf_counter()
    print(f"asyncio: total busy time: {total_end - total_start - 5:.4f} seconds")


async def bench_w_connection_pool_reuse():
    total_start = time.perf_counter()

    connector = aiohttp.TCPConnector(limit=100, limit_per_host=20)
    async with aiohttp.ClientSession(connector=connector) as session:
        for _ in range(5):
            start = time.perf_counter()
            
            tasks = []
            results = []
            for url in URLS:
                task = asyncio.create_task(fetch_and_store(session, url, results))
                tasks.append(task)
            
            await asyncio.gather(*tasks)

            successful = [r for r in results if r["status"] == 200]

            end = time.perf_counter()

            print(f"asyncio: fetched {len(URLS)} URLs in {end - start:.4f} seconds (successful: {len(successful)}/{len(URLS)})")

            await asyncio.sleep(1)

    total_end = time.perf_counter()
    print(f"asyncio: total busy time: {total_end - total_start - 5:.4f} seconds")


async def main():
    print("=" * 50)
    print("asyncio bench with session creation per request")
    await bench_w_session_creation()

    print("=" * 50)
    print("asyncio bench with connection pool reuse")
    await bench_w_connection_pool_reuse()


if __name__ == "__main__":
    asyncio.run(main())
