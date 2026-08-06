package leetcode

//
// @lc app=leetcode id=3821 lang=golang
//
// [3821] Find N-th Smallest Integer With K One Bits
//
// Notes
// Build the answer from high bit to low bit in combinatorial order. With a zero
// at bit b, there are C(b, remainingOnes) smaller completions; skip them by
// setting the bit when n is larger. The binomial helper is small and exact for
// the 50-bit search space used by the Python solution. Time: O(50*k). Space:
// O(1).
//
// @lc code=start

func NthSmallest3821(n int, k int) int {
	answer := 0
	remaining := k
	for bit := 49; bit >= 0; bit-- {
		countWithZero := comb3821(bit, remaining)
		if n > countWithZero {
			n -= countWithZero
			answer |= 1 << bit
			remaining--
			if remaining == 0 {
				break
			}
		}
	}
	return answer
}

func comb3821(n, r int) int {
	if r < 0 || r > n {
		return 0
	}
	if r > n-r {
		r = n - r
	}
	result := 1
	for i := 1; i <= r; i++ {
		result = result * (n - r + i) / i
	}
	return result
}

// @lc code=end
