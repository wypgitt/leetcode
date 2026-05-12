package main

func movesToMakeZigzag(nums []int) int {
	n := len(nums)

	costForValleys := func(parity int) int {
		moves := 0
		for i, value := range nums {
			if i%2 != parity {
				continue
			}
			allowed := 1 << 30
			if i > 0 && nums[i-1]-1 < allowed {
				allowed = nums[i-1] - 1
			}
			if i+1 < n && nums[i+1]-1 < allowed {
				allowed = nums[i+1] - 1
			}
			if value > allowed {
				moves += value - allowed
			}
		}
		return moves
	}

	evenCost, oddCost := costForValleys(0), costForValleys(1)
	if evenCost < oddCost {
		return evenCost
	}
	return oddCost
}

