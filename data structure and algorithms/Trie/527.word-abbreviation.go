package leetcode

//
// @lc app=leetcode id=527 lang=golang
//
// [527] Word Abbreviation
//
// Notes
// Start every word with prefix length 1. Repeatedly group words by their current
// abbreviation; whenever a group conflicts, increase the prefix length for all
// words in that group. When no group conflicts, abbreviations are unique and
// still as short as this incremental process permits. Time: O(rounds*n*L).
// Space: O(nL).
//
// @lc code=start

import "strconv"

func WordsAbbreviation527(words []string) []string {
	prefixLengths := make([]int, len(words))
	for i := range prefixLengths {
		prefixLengths[i] = 1
	}

	for {
		groups := map[string][]int{}
		for index, word := range words {
			abbr := abbreviate527(word, prefixLengths[index])
			groups[abbr] = append(groups[abbr], index)
		}

		hasConflict := false
		for _, indices := range groups {
			if len(indices) <= 1 {
				continue
			}
			hasConflict = true
			for _, index := range indices {
				prefixLengths[index]++
			}
		}
		if !hasConflict {
			break
		}
	}

	answer := make([]string, len(words))
	for index, word := range words {
		answer[index] = abbreviate527(word, prefixLengths[index])
	}
	return answer
}

func abbreviate527(word string, prefixLength int) string {
	omitted := len(word) - prefixLength - 1
	abbreviation := word[:prefixLength] + strconv.Itoa(omitted) + word[len(word)-1:]
	if len(abbreviation) < len(word) {
		return abbreviation
	}
	return word
}

// @lc code=end
