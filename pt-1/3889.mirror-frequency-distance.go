package leetcode

//
// @lc app=leetcode id=3889 lang=golang
//
// [3889] Mirror Frequency Distance
//
// Notes
// Count characters, then compare mirrored lowercase letters a/z through m/n and
// mirrored digits 0/9 through 4/5. The answer is the sum of absolute frequency
// differences. A fixed byte-frequency array is enough in Go. Time: O(n). Space:
// O(1).
//
// @lc code=start

func MirrorFrequency3889(s string) int {
	frequency := [256]int{}
	for i := range s {
		frequency[s[i]]++
	}

	answer := 0
	for offset := 0; offset < 13; offset++ {
		left := byte('a' + offset)
		right := byte('z' - offset)
		answer += abs3889(frequency[left] - frequency[right])
	}
	for offset := 0; offset < 5; offset++ {
		left := byte('0' + offset)
		right := byte('9' - offset)
		answer += abs3889(frequency[left] - frequency[right])
	}
	return answer
}

func abs3889(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// @lc code=end
