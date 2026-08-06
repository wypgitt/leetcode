package leetcode

// LengthOfLongestSubstringTwoDistinct159 is a sliding window with a character
// count map. The left side shrinks only while the window has more than two
// distinct characters.
//
// Time: O(n). Space: O(1) for bounded alphabet, O(k) generally.
func LengthOfLongestSubstringTwoDistinct159(s string) int {
	counts := map[byte]int{}
	left, best := 0, 0
	for right := 0; right < len(s); right++ {
		counts[s[right]]++
		for len(counts) > 2 {
			old := s[left]
			counts[old]--
			if counts[old] == 0 {
				delete(counts, old)
			}
			left++
		}
		best = maxInt(best, right-left+1)
	}
	return best
}
