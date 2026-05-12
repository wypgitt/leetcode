package main

/*
1023. Camelcase Matching
*/
func camelMatch(queries []string, pattern string) []bool {
	answer := make([]bool, len(queries))

	for i, query := range queries {
		answer[i] = camelMatches(query, pattern)
	}

	return answer
}

func camelMatches(query, pattern string) bool {
	patternIndex := 0

	for i := 0; i < len(query); i++ {
		current := query[i]
		if patternIndex < len(pattern) && current == pattern[patternIndex] {
			patternIndex++
		} else if current >= 'A' && current <= 'Z' {
			return false
		}
	}

	return patternIndex == len(pattern)
}

/*
Interview Explanation

Core idea:
A query matches if it is the pattern with lowercase letters inserted anywhere.
Extra lowercase letters are allowed. Extra uppercase letters are not allowed.

Go data structures:
- []bool stores answers in query order.
- An integer pointer into pattern is enough because the problem is an ordered
  subsequence match with one extra uppercase rule.

Algorithm:
For each query:
1. Scan bytes left to right.
2. If the byte equals the next pattern byte, consume it.
3. Otherwise, if it is uppercase, reject the query.
4. Otherwise it is an inserted lowercase letter, so ignore it.
5. Accept only if the whole pattern was consumed.

Correctness:
The scan uses pattern characters in order and ignores only lowercase inserted
characters, exactly matching the allowed operation. If an unmatched uppercase
letter appears, it could not have been inserted, so rejection is required. If
the pattern pointer reaches the end, every required character was matched in
order.

Complexity:
Let T be the total length of all queries. Time is O(T). Extra space is O(1)
besides the output slice.

Edge cases:
- Exact pattern match returns true.
- Extra lowercase letters around pattern letters are fine.
- Extra uppercase letters return false.
- Missing pattern letters return false.
*/
