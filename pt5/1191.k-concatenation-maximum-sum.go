package main

func kConcatenationMaxSum(arr []int, k int) int {
	const mod int64 = 1_000_000_007

	kadane := func(times int) int64 {
		best, current := int64(0), int64(0)
		for t := 0; t < times; t++ {
			for _, value := range arr {
				current += int64(value)
				if current < 0 {
					current = 0
				}
				if current > best {
					best = current
				}
			}
		}
		return best
	}

	if k == 1 {
		return int(kadane(1) % mod)
	}

	best := kadane(2)
	total := int64(0)
	for _, value := range arr {
		total += int64(value)
	}
	if total > 0 {
		best += int64(k-2) * total
	}
	return int(best % mod)
}
