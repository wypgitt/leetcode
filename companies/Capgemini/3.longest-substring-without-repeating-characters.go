package leetcode

// LengthOfLongestSubstring3 uses a sliding window with a map from byte to last
// seen index. When a duplicate lies inside the current window, left jumps past
// the previous occurrence; max is needed for cases like "abba".
//
// Time: O(n). Space: O(min(n, alphabet)).
func LengthOfLongestSubstring3(s string) int {
	last := map[byte]int{}
	left, best := 0, 0
	for right := 0; right < len(s); right++ {
		ch := s[right]
		if old, ok := last[ch]; ok && old >= left {
			left = old + 1
		}
		last[ch] = right
		best = maxInt(best, right-left+1)
	}
	return best
}
