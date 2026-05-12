package main

import "math/bits"

func maxLength(arr []string) int {
	masks := []int{0}
	best := 0

	for _, word := range arr {
		mask := 0
		valid := true
		for i := 0; i < len(word); i++ {
			bit := 1 << (word[i] - 'a')
			if mask&bit != 0 {
				valid = false
				break
			}
			mask |= bit
		}
		if !valid {
			continue
		}

		currentCount := len(masks)
		for i := 0; i < currentCount; i++ {
			if masks[i]&mask == 0 {
				combined := masks[i] | mask
				masks = append(masks, combined)
				if length := bits.OnesCount(uint(combined)); length > best {
					best = length
				}
			}
		}
	}

	return best
}

/*
Explanation

Represent a word as a 26-bit mask. Words with duplicate letters are discarded.
A word can be appended to an existing concatenation exactly when their masks
have no common bit: existing&mask == 0.

Bit masks are the key Go data structure here because overlap checks become
constant-time integer operations. The masks slice stores all achievable
concatenations from processed words. We iterate only over the old length of the
slice so the current word is not reused.

Edge cases: every word invalid gives 0; shared letters block combination;
bits.OnesCount gives the length of a valid combined mask.

Time complexity: O(n * 2^n) in the worst case.
Space complexity: O(2^n).
*/
