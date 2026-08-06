package leetcode

//
// @lc app=leetcode id=411 lang=golang
//
// [411] Minimum Unique Word Abbreviation
//
// Notes
// Only dictionary words with the target length matter. For each such word,
// build a bitmask of positions where it differs from target. An abbreviation
// mask is valid iff it keeps at least one differing character for every word.
// Enumerate masks, compute abbreviation length, keep the shortest, and build the
// final abbreviation. Time: O(2^m * (m+d)). Space: O(d), m=len(target).
//
// @lc code=start

import "strconv"

func MinAbbreviation411(target string, dictionary []string) string {
	wordLength := len(target)
	relevant := []string{}
	for _, word := range dictionary {
		if len(word) == wordLength {
			relevant = append(relevant, word)
		}
	}
	if len(relevant) == 0 {
		return strconv.Itoa(wordLength)
	}

	differenceMasks := make([]int, 0, len(relevant))
	for _, word := range relevant {
		difference := 0
		for index := 0; index < wordLength; index++ {
			if target[index] != word[index] {
				difference |= 1 << index
			}
		}
		differenceMasks = append(differenceMasks, difference)
	}

	abbreviationLength := func(mask int) int {
		length := 0
		index := 0
		for index < wordLength {
			length++
			if mask&(1<<index) != 0 {
				index++
			} else {
				for index < wordLength && mask&(1<<index) == 0 {
					index++
				}
			}
		}
		return length
	}

	buildAbbreviation := func(mask int) string {
		parts := []byte{}
		abbreviatedCount := 0
		for index := 0; index < wordLength; index++ {
			if mask&(1<<index) != 0 {
				if abbreviatedCount > 0 {
					parts = append(parts, strconv.Itoa(abbreviatedCount)...)
					abbreviatedCount = 0
				}
				parts = append(parts, target[index])
			} else {
				abbreviatedCount++
			}
		}
		if abbreviatedCount > 0 {
			parts = append(parts, strconv.Itoa(abbreviatedCount)...)
		}
		return string(parts)
	}

	bestMask := (1 << wordLength) - 1
	bestLength := wordLength
	for mask := 0; mask < 1<<wordLength; mask++ {
		currentLength := abbreviationLength(mask)
		if currentLength >= bestLength {
			continue
		}
		valid := true
		for _, difference := range differenceMasks {
			if mask&difference == 0 {
				valid = false
				break
			}
		}
		if valid {
			bestMask = mask
			bestLength = currentLength
		}
	}

	return buildAbbreviation(bestMask)
}

// @lc code=end
