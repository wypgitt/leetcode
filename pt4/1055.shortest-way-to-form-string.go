package main

import "sort"

/*
1055. Shortest Way to Form String
*/
func shortestWay(source string, target string) int {
	positions := make([][]int, 26)
	for i := 0; i < len(source); i++ {
		letter := source[i] - 'a'
		positions[letter] = append(positions[letter], i)
	}

	subsequences := 1
	currentIndex := -1

	for i := 0; i < len(target); i++ {
		letter := target[i] - 'a'
		indexes := positions[letter]
		if len(indexes) == 0 {
			return -1
		}

		next := sort.Search(len(indexes), func(j int) bool {
			return indexes[j] > currentIndex
		})

		if next == len(indexes) {
			subsequences++
			currentIndex = indexes[0]
		} else {
			currentIndex = indexes[next]
		}
	}

	return subsequences
}

/*
Interview Explanation

Core idea:
Build each subsequence greedily by taking the earliest possible source
occurrence for each target character. If the next character cannot appear
after the current source index, start a new subsequence.

Go data structures:
- [][]int positions stores sorted source indices for each lowercase letter.
- sort.Search performs binary search for the first index greater than the
  current source position.

Algorithm:
1. Precompute every source index for each character.
2. Scan target left to right.
3. If a character never appears in source, return -1.
4. Binary search for the next occurrence after currentIndex.
5. If none exists, start a new subsequence and use the first occurrence.

Correctness:
Choosing the earliest possible occurrence leaves the most room for future
characters in the current subsequence, so it can never hurt. A new subsequence
is started exactly when the current one cannot contain the next target
character. Therefore the greedy count is minimal.

Complexity:
Preprocessing is O(len(source)). Each target character uses binary search, so
time is O(len(target) log len(source)). Space is O(len(source)).

Edge cases:
- Missing target character returns -1.
- Target already a subsequence returns 1.
- Repeated wraparounds are counted correctly.
*/
