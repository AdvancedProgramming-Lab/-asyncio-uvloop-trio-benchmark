import trio
import httpx
import time

URLS = ["http://localhost:1880" for _ in range(50)]


async def fetch(client, url):
    try:
        resp = await client.get(url, timeout=10.0)
        return {"url": url, "status": resp.status_code, "error": None}
    except Exception as e:
        return {"url": url, "status": None, "error": str(e)}


async def fetch_and_store(client, url, results):
    result = await fetch(client, url)
    results.append(result)


async def bench_w_session_creation():
    total_start = time.perf_counter()

    for _ in range(5):
        start = time.perf_counter()
        async with httpx.AsyncClient() as client:
            async with trio.open_nursery() as nursery:
                results = []
                for url in URLS:
                    nursery.start_soon(fetch_and_store, client, url, results)

        successful = [r for r in results if r["status"] == 200]

        end = time.perf_counter()

        print(f"trio: fetched {len(URLS)} URLs in {end - start:.4f} seconds (sucessful: {len(successful)}/{len(URLS)})")

        await trio.sleep(1)

    total_end = time.perf_counter()
    print(f"trio: total busy time: {total_end - total_start - 5:.4f} seconds")


async def bench_w_connection_pool_reuse():
    total_start = time.perf_counter()

    async with httpx.AsyncClient(
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
    ) as client:
        for _ in range(5):
            start = time.perf_counter()
            async with trio.open_nursery() as nursery:
                results = []
                for url in URLS:
                    nursery.start_soon(fetch_and_store, client, url, results)

            successful = [r for r in results if r["status"] == 200]

            end = time.perf_counter()

            print(f"trio: fetched {len(URLS)} URLs in {end - start:.4f} seconds (sucessful: {len(successful)}/{len(URLS)})")

            await trio.sleep(1)

    total_end = time.perf_counter()
    print(f"trio: total busy time: {total_end - total_start - 5:.4f} secodns")


if __name__ == "__main__":
    print("=" * 50)
    print("trio bench with session creation per request")
    trio.run(bench_w_session_creation)

    print("=" * 50)
    print("trio bench with connection pool reuse")
    trio.run(bench_w_connection_pool_reuse)
