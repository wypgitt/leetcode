package leetcode

// MinimumLengthEncoding820 removes every proper suffix from the useful word set.
// Remaining words are exactly those that need explicit encoding plus '#'.
//
// Go data structure note: map[string]bool acts as a hash set and also
// deduplicates repeated words.
//
// Time: O(sum len(word)^2) if substring cost is counted. Space: O(total length).
func MinimumLengthEncoding820(words []string) int {
	useful := map[string]bool{}
	for _, w := range words {
		useful[w] = true
	}
	for _, word := range words {
		for i := 1; i < len(word); i++ {
			delete(useful, word[i:])
		}
	}
	ans := 0
	for word := range useful {
		ans += len(word) + 1
	}
	return ans
}
