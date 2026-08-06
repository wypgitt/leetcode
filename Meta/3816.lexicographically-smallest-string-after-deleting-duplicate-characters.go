package leetcode

//
// @lc app=leetcode id=3816 lang=golang
//
// [3816] Lexicographically Smallest String After Deleting Duplicate Characters
//
// Notes
// This is a greedy subsequence construction with one required copy of every
// distinct character. Try letters from 'a' to 'z' at the current start; choose
// the first occurrence that still leaves a future occurrence of every missing
// character. Position lists plus moving pointers make each candidate lookup
// efficient. Time: O(26^2 + n). Space: O(n).
//
// @lc code=start

func LexSmallestAfterDeletion3816(s string) string {
	positions := make([][]int, 26)
	for index, ch := range []byte(s) {
		positions[int(ch-'a')] = append(positions[int(ch-'a')], index)
	}

	last := make([]int, 26)
	for i := range last {
		last[i] = -1
	}
	missing := 0
	for ch := 0; ch < 26; ch++ {
		if len(positions[ch]) > 0 {
			last[ch] = positions[ch][len(positions[ch])-1]
			missing |= 1 << ch
		}
	}

	ptr := make([]int, 26)
	start := 0
	answer := make([]byte, 0, 26)

	for missing != 0 {
		for ch := 0; ch < 26; ch++ {
			posList := positions[ch]
			for ptr[ch] < len(posList) && posList[ptr[ch]] < start {
				ptr[ch]++
			}
			if ptr[ch] == len(posList) {
				continue
			}

			index := posList[ptr[ch]]
			newMissing := missing &^ (1 << ch)
			if canFinishAfter3816(index, newMissing, last) {
				answer = append(answer, byte('a'+ch))
				start = index + 1
				missing = newMissing
				break
			}
		}
	}

	return string(answer)
}

func canFinishAfter3816(index int, missing int, last []int) bool {
	for ch := 0; ch < 26; ch++ {
		if ((missing>>ch)&1) == 1 && last[ch] <= index {
			return false
		}
	}
	return true
}

// @lc code=end
