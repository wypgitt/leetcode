package leetcode

//
// @lc app=leetcode id=514 lang=golang
//
// [514] Freedom Trail
//
// Notes
// Store all ring positions for each character. DP maps the current ring index to
// the minimum cost after spelling the processed key prefix. For each next
// character, try every target occurrence and every current index, paying the
// shorter circular rotation plus one button press. Time: O(|key| * P^2) in the
// worst case. Space: O(P).
//
// @lc code=start

func FindRotateSteps514(ring string, key string) int {
	ringLength := len(ring)
	positions := map[byte][]int{}
	for index := range ring {
		positions[ring[index]] = append(positions[ring[index]], index)
	}

	dp := map[int]int{0: 0}
	for index := range key {
		ch := key[index]
		nextDP := map[int]int{}
		for _, target := range positions[ch] {
			best := 1 << 60
			for current, currentCost := range dp {
				directDistance := abs514(current - target)
				rotationCost := min514(directDistance, ringLength-directDistance)
				if candidate := currentCost + rotationCost + 1; candidate < best {
					best = candidate
				}
			}
			nextDP[target] = best
		}
		dp = nextDP
	}

	answer := 1 << 60
	for _, value := range dp {
		if value < answer {
			answer = value
		}
	}
	return answer
}

func abs514(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func min514(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// @lc code=end
