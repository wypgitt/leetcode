package leetcode

// ShortestWordDistance245 handles equal words by tracking the previous occurrence
// of that same word. For different words, it tracks the latest index of each word
// and updates the best distance whenever the other has been seen.
//
// Time: O(n). Space: O(1).
func ShortestWordDistance245(wordsDict []string, word1 string, word2 string) int {
	best := 1<<31 - 1
	if word1 == word2 {
		prev := -1
		for i, w := range wordsDict {
			if w == word1 {
				if prev != -1 {
					best = minInt(best, i-prev)
				}
				prev = i
			}
		}
		return best
	}
	last1, last2 := -1, -1
	for i, w := range wordsDict {
		if w == word1 {
			last1 = i
			if last2 != -1 {
				best = minInt(best, absInt(last1-last2))
			}
		} else if w == word2 {
			last2 = i
			if last1 != -1 {
				best = minInt(best, absInt(last1-last2))
			}
		}
	}
	return best
}
