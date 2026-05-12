package main

func longestWPI(hours []int) int {
	firstSeen := map[int]int{}
	score, best := 0, 0

	for i, hour := range hours {
		if hour > 8 {
			score++
		} else {
			score--
		}

		if score > 0 {
			best = i + 1
		} else if index, ok := firstSeen[score-1]; ok && i-index > best {
			best = i - index
		}

		if _, ok := firstSeen[score]; !ok {
			firstSeen[score] = i
		}
	}

	return best
}

