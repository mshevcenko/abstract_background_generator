import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor

ctx = multiprocessing.get_context("spawn")
process_executor = ProcessPoolExecutor(
    mp_context=ctx,
    max_workers=os.cpu_count()
)