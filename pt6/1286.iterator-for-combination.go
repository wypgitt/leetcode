package main

type CombinationIterator struct {
	combinations []string
	index        int
}

func Constructor(characters string, combinationLength int) CombinationIterator {
	it := CombinationIterator{}
	var dfs func(int, []byte)
	dfs = func(start int, path []byte) {
		if len(path) == combinationLength {
			it.combinations = append(it.combinations, string(append([]byte(nil), path...)))
			return
		}
		need := combinationLength - len(path)
		for i := start; i <= len(characters)-need; i++ {
			path = append(path, characters[i])
			dfs(i+1, path)
			path = path[:len(path)-1]
		}
	}
	dfs(0, []byte{})
	return it
}

func (it *CombinationIterator) Next() string {
	value := it.combinations[it.index]
	it.index++
	return value
}

func (it *CombinationIterator) HasNext() bool {
	return it.index < len(it.combinations)
}

/*
Explanation

Precompute all combinations in lexicographic order using DFS. Since the input
characters are already sorted, choosing increasing indices produces sorted
combinations. The iterator then only needs an index.

Precomputation is a good design tradeoff for the constraints: Next and HasNext
become O(1), and the number of combinations is small.

Go detail: when converting path to string, append([]byte(nil), path...) copies
the current path so later backtracking mutations do not affect stored data.

Edge cases: only one combination; repeated HasNext calls do not advance; Next
advances exactly once.

Constructor time and space: O(C*L), where C is number of combinations and L is
combinationLength. Next and HasNext: O(1).
*/
