package leetcode

//
// @lc app=leetcode id=3871 lang=golang
//
// [3871] Count Commas in Range II
//
// Notes
// Numbers from 1,000 to 999,999 each contribute one comma, the next thousand
// block contributes two, and so on. Scan powers of 1000 and add the block size
// times its comma count. Time: O(log_1000 n). Space: O(1).
//
// @lc code=start

func CountCommas3871(n int) int {
	answer := 0
	start := 1000
	commas := 1

	for start <= n {
		end := start*1000 - 1
		actualEnd := end
		if actualEnd > n {
			actualEnd = n
		}
		answer += (actualEnd - start + 1) * commas
		start *= 1000
		commas++
	}

	return answer
}

// @lc code=end
