import cProfile
import pstats
from main import run_app  # <-- tumhare main loop ko function banake import karenge

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    run_app()  # Tumhara camera loop wala function

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.dump_stats("profile_results.prof")
