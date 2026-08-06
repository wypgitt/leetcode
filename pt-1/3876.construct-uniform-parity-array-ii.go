package leetcode

//
// @lc app=leetcode id=3876 lang=golang
//
// [3876] Construct Uniform Parity Array II
//
// Notes
// If all numbers have the same parity, the array is already uniform. Otherwise
// the Python criterion is exactly whether the minimum odd value is smaller than
// the minimum even value. We track both minima in one pass. Time: O(n). Space:
// O(1).
//
// @lc code=start

func UniformArray3876(nums1 []int) bool {
	const inf = 1 << 60
	minOdd := inf
	minEven := inf

	for _, value := range nums1 {
		if value%2 != 0 {
			if value < minOdd {
				minOdd = value
			}
		} else if value < minEven {
			minEven = value
		}
	}

	if minOdd == inf || minEven == inf {
		return true
	}
	return minOdd < minEven
}

// @lc code=end
