package leetcode

//
// @lc app=leetcode id=3913 lang=golang
//
// [3913] Sort Vowels by Frequency
//
// Notes
// Count lowercase vowels and remember each vowel's first occurrence. Sort the
// vowel characters by descending frequency and then first occurrence, stream the
// sorted repeated vowels back into the original vowel positions, and leave all
// consonants unchanged. Time: O(n + V log V). Space: O(n).
//
// @lc code=start

import "sort"

func SortVowels3913(s string) string {
	count := [256]int{}
	first := [256]int{}
	for i := range first {
		first[i] = -1
	}

	for index := 0; index < len(s); index++ {
		ch := s[index]
		if isVowel3913(ch) {
			count[ch]++
			if first[ch] == -1 {
				first[ch] = index
			}
		}
	}

	vowels := []byte{}
	for _, ch := range []byte{'a', 'e', 'i', 'o', 'u'} {
		if count[ch] > 0 {
			vowels = append(vowels, ch)
		}
	}
	sort.Slice(vowels, func(i, j int) bool {
		if count[vowels[i]] != count[vowels[j]] {
			return count[vowels[i]] > count[vowels[j]]
		}
		return first[vowels[i]] < first[vowels[j]]
	})

	stream := []byte{}
	for _, ch := range vowels {
		for i := 0; i < count[ch]; i++ {
			stream = append(stream, ch)
		}
	}

	chars := []byte(s)
	streamIndex := 0
	for index, ch := range chars {
		if isVowel3913(ch) {
			chars[index] = stream[streamIndex]
			streamIndex++
		}
	}

	return string(chars)
}

func isVowel3913(ch byte) bool {
	return ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u'
}

// @lc code=end
