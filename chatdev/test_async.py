import asyncio

async def lol():
    await asyncio.sleep(10)



async def run_coroutine_with_timeout():
    try:
        await asyncio.wait_for(lol(), timeout=1)
    except asyncio.TimeoutError:
        print(f"Coroutine exceeded timeout, rerunning...")
        await lol()


asyncio.run(run_coroutine_with_timeout())