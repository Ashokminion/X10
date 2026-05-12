import asyncio

async def main():
    print("Asyncio is working!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Asyncio failed: {e}")
