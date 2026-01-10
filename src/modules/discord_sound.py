import asyncio

async def run_discord_loop():
    while True:
        await asyncio.sleep(1) # Sleep to keep the CPU usage low

if __name__ == "__main__":
    try:
        asyncio.run(run_discord_loop())
    except KeyboardInterrupt:
        pass