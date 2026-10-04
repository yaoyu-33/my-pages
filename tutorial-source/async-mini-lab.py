# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""A standard-library-only async lesson. No HTTP, Gym, GPU or subprocesses.

Run: python3 async-mini-lab.py
Predict peak_in_flight first: sequential=1, scheduled=4, bounded=2, blocking=1.
The counter includes waiting operations; it does not count CPUs or threads.
Elapsed seconds are illustrative measurements, never benchmark assertions.
"""

import asyncio
import json
import time


async def run_case(mode: str) -> dict[str, object]:
    in_flight = 0
    peak_in_flight = 0
    events: list[str] = []
    semaphore = asyncio.Semaphore(2)

    async def operation(name: str) -> None:
        nonlocal in_flight, peak_in_flight
        in_flight += 1
        peak_in_flight = max(peak_in_flight, in_flight)
        events.append(f"{name}:start")
        try:
            if mode == "blocking":
                time.sleep(0.12)  # Deliberate anti-example: occupies the loop's thread.
            else:
                await asyncio.sleep(0.12)  # Simulates waiting; no actual network I/O.
        finally:
            events.append(f"{name}:end")
            in_flight -= 1

    async def bounded(name: str) -> None:
        async with semaphore:
            await operation(name)

    started = time.perf_counter()
    if mode == "sequential":
        for name in "ABCD":
            await operation(name)
    elif mode == "scheduled":
        tasks = [asyncio.create_task(operation(name)) for name in "ABCD"]
        for task in tasks:
            await task  # Already scheduled: these await statements do not serialize starts.
    else:
        worker = bounded if mode == "bounded" else operation
        await asyncio.gather(*(worker(name) for name in "ABCD"))
    return {
        "mode": mode,
        "peak_in_flight": peak_in_flight,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "events": events,
    }


async def main() -> None:
    entered: list[bool] = []

    async def probe() -> None:
        entered.append(True)

    coroutine = probe()  # Creates a coroutine object, without scheduling its body.
    await asyncio.sleep(0)
    print(json.dumps({"created_coroutine_has_started": bool(entered)}))
    await coroutine  # Consume it, so no unawaited-coroutine warning remains.
    for mode in ("sequential", "scheduled", "bounded", "blocking"):
        print(json.dumps(await run_case(mode)))


if __name__ == "__main__":
    asyncio.run(main())
