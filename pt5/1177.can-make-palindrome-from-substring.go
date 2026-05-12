package main

import "math/bits"

func canMakePaliQueries(s string, queries [][]int) []bool {
	prefix := make([]int, len(s)+1)
	mask := 0
	for i := 0; i < len(s); i++ {
		mask ^= 1 << int(s[i]-'a')
		prefix[i+1] = mask
	}

	answer := make([]bool, len(queries))
	for i, query := range queries {
		left, right, k := query[0], query[1], query[2]
		oddMask := prefix[right+1] ^ prefix[left]
		answer[i] = bits.OnesCount(uint(oddMask))/2 <= k
	}
	return answer
}

