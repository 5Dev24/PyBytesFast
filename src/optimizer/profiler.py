from time import process_time
from os import devnull
from types import CodeType
from typing import List, Tuple
from quantiphy import Quantity
import sys

def _average_of(items: list):
	return sum(items) / len(items)

# Remove large deviations from data
def _refine(items: list) -> List[object]:
	# Calculate the standard deviation
	average = _average_of(items)
	sum_of_squared_deviations = 0
	for item in items:
		sum_of_squared_deviations += (item - average) ** 2
	standard_deviation = (sum_of_squared_deviations / len(items)) ** 0.5
	del average, sum_of_squared_deviations

	# Purge items
	return [item for item in items if abs(item - average) < standard_deviation]

# Profiles compiled code and calculates statistics about the runtimes
# If tolerance <= 0: returns min, max, and average
# Else returns min, max, average, # of close to min speeds, # of close to max speeds
def profile(compiled_code: CodeType, runs: int = 512, tolerance: float = 5, refinements: int = 1) -> Tuple[float]:
	"""

	"""

	speeds: List[float] = []

	with open(devnull, "w") as null:
		# Remove any output from code
		saved_stdout = sys.stdout
		saved_stderr = sys.stderr
		try:
			sys.stdout = sys.stderr = null

			for _ in range(runs):
				start_time = process_time()
				exec(compiled_code) # Unsafe
				end_time = process_time()
				speeds.append(end_time - start_time)

		finally:
			sys.stdout = saved_stdout
			sys.stderr = saved_stderr

	for _ in range(refinements):
		speeds = _refine(speeds)

	min_speed = min(speeds)
	max_speed = max(speeds)

	if tolerance > 0:
		close_to_min_speed = 0
		close_to_max_speed = 0

		speed_range = max_speed - min_speed # Range
		max_percent = max_speed - speed_range * (tolerance / 100.0) # Max - Tolerance * Range
		min_percent = min_speed + speed_range * (tolerance / 100.0) # Min + Tolerance * Range

		for speed in speeds:
			if speed < min_percent:
				close_to_min_speed += 1
			elif speed > max_percent:
				close_to_max_speed += 1

		return (min_speed, max_speed, _average_of(speeds), close_to_min_speed, close_to_max_speed)

	return (min_speed, max_speed, _average_of(speeds))