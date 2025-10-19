import time
from statistics import mean
from dotenv import load_dotenv
from app.services.animals import top_breeds, age_histogram

def bench(label, fn, *args, loops=5, warmup=1, **kwargs):
    # warmup
    for _ in range(warmup):
        fn(*args, **kwargs)
    times = []
    for _ in range(loops):
        t0 = time.perf_counter()
        fn(*args, **kwargs)
        times.append(time.perf_counter() - t0)
    print(f"{label}: {mean(times)*1000:.2f} ms avg over {loops} runs")

def main():
    load_dotenv()
    filters = {"animal_type": {"$in": ["Dog"]}}
    print("=== Aggregation benchmarks (cached vs first-run) ===")
    # first call (no cache)
    bench("top_breeds cold ", top_breeds, filters)
    # cached calls
    bench("top_breeds cached", top_breeds, filters)
    bench("age_hist cold    ", age_histogram, filters)
    bench("age_hist cached  ", age_histogram, filters)

if __name__ == "__main__":
    main()