package main

func maxFreq(s string, maxLetters int, minSize int, maxSize int) int {
	window := map[byte]int{}
	distinct := 0
	freq := map[string]int{}
	best := 0

	for right := 0; right < len(s); right++ {
		ch := s[right]
		if window[ch] == 0 {
			distinct++
		}
		window[ch]++

		if right >= minSize {
			leftCh := s[right-minSize]
			window[leftCh]--
			if window[leftCh] == 0 {
				distinct--
			}
		}

		if right >= minSize-1 && distinct <= maxLetters {
			sub := s[right-minSize+1 : right+1]
			freq[sub]++
			if freq[sub] > best {
				best = freq[sub]
			}
		}
	}

	return best
}

/*
Explanation

It is enough to count substrings of length minSize. Any longer valid substring
has a minSize prefix that appears at least as often, so the maximum frequency
is achieved by some minSize substring.

Use a fixed-size sliding window and a byte-count map to maintain the number of
distinct letters. When the window length is minSize and distinct <= maxLetters,
count that substring in a frequency map.

maxSize is not used because of the prefix argument above.

Edge cases: maxLetters == 1; overlapping repeated substrings; no valid window
returns 0.

Time complexity: O(n * minSize) because slicing a string key may require
hashing the substring content.
Space complexity: O(n * minSize) for distinct substring keys.
*/
