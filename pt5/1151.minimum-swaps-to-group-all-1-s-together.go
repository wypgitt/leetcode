package main

func minSwaps(data []int) int {
	ones := 0
	for _, value := range data {
		ones += value
	}
	if ones <= 1 {
		return 0
	}

	zeros := 0
	for i := 0; i < ones; i++ {
		if data[i] == 0 {
			zeros++
		}
	}
	best := zeros
	for right := ones; right < len(data); right++ {
		if data[right] == 0 {
			zeros++
		}
		if data[right-ones] == 0 {
			zeros--
		}
		if zeros < best {
			best = zeros
		}
	}
	return best
}

