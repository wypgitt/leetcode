package main

import "sort"

/*
1048. Longest String Chain
*/
func longestStrChain(words []string) int {
	sort.Slice(words, func(i, j int) bool {
		return len(words[i]) < len(words[j])
	})

	bestEndingAt := make(map[string]int)
	answer := 1

	for _, word := range words {
		best := 1
		for i := 0; i < len(word); i++ {
			predecessor := word[:i] + word[i+1:]
			if bestEndingAt[predecessor]+1 > best {
				best = bestEndingAt[predecessor] + 1
			}
		}
		bestEndingAt[word] = best
		if best > answer {
			answer = best
		}
	}

	return answer
}

/*
Interview Explanation

Core idea:
If wordA is a predecessor of wordB, wordA can be made by deleting exactly one
character from wordB. Process shorter words first, then look up all deletion
candidates.

Go data structures:
- sort.Slice orders words by length.
- map[string]int stores the best chain length ending at each word.

Algorithm:
1. Sort words by length.
2. For each word, delete each character once to form predecessor candidates.
3. If a predecessor exists in the map, extend its chain.
4. Store the best chain length for the current word.

Correctness:
Every valid chain ending at a word must come from a predecessor formed by one
deletion. The algorithm tries every such predecessor and uses the best already
computed chain. Sorting by length guarantees all predecessors are processed
before the current word.

Complexity:
Let n be the number of words and L be max word length. Sorting costs
O(n log n). Creating deletion strings costs O(L) each for up to L deletions per
word, so DP work is O(n*L^2). Space is O(n).

Edge cases:
- No valid chain returns 1.
- Multiple predecessors are resolved by max.
- Same-length words cannot be predecessors.
*/
