package leetcode

//
// @lc app=leetcode id=3891 lang=golang
//
// [3891] Minimum Increase to Maximize Special Indices
//
// Notes
// Dynamic programming over candidate peak positions. take means the previous
// index was chosen as a special peak; skip means it was not. Since adjacent
// peaks cannot both be chosen, a new take can only come from skip. Pairs store
// (peak count, cost), and comparison maximizes count then minimizes cost.
// Time: O(n). Space: O(1).
//
// @lc code=start

type scoreCost3891 struct {
	score int
	cost  int
}

func MinIncrease3891(nums []int) int {
	better := func(first, second scoreCost3891) scoreCost3891 {
		if first.score != second.score {
			if first.score > second.score {
				return first
			}
			return second
		}
		if first.cost <= second.cost {
			return first
		}
		return second
	}

	take := scoreCost3891{score: -1 << 60, cost: 0}
	skip := scoreCost3891{score: 0, cost: 0}

	for index := 1; index < len(nums)-1; index++ {
		peakCost := max3891(0, max3891(nums[index-1], nums[index+1])+1-nums[index])
		newTake := scoreCost3891{score: skip.score + 1, cost: skip.cost + peakCost}
		newSkip := better(take, skip)
		take, skip = newTake, newSkip
	}

	return better(take, skip).cost
}

func max3891(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// @lc code=end
