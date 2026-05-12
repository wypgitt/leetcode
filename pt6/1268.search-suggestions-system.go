package main

import "sort"

func suggestedProducts(products []string, searchWord string) [][]string {
	sort.Strings(products)
	ans := make([][]string, 0, len(searchWord))
	prefix := ""

	for i := 0; i < len(searchWord); i++ {
		prefix += string(searchWord[i])
		start := sort.SearchStrings(products, prefix)
		suggestions := []string{}
		for j := start; j < len(products) && j < start+3; j++ {
			if hasPrefix(products[j], prefix) {
				suggestions = append(suggestions, products[j])
			}
		}
		ans = append(ans, suggestions)
	}

	return ans
}

func hasPrefix(word, prefix string) bool {
	return len(word) >= len(prefix) && word[:len(prefix)] == prefix
}

/*
Explanation

Sort products lexicographically. For each search prefix, binary search for the
first product not less than the prefix, then inspect at most the next three
products and keep those that actually start with the prefix.

Sorting works because all words with a common prefix occupy a contiguous range,
and the first three in that range are the lexicographically smallest
suggestions. This is a compact alternative to a trie.

Edge cases: fewer than three matches; no matches; one product being a prefix of
another.

Time complexity: O(n log n + m log n + 3mL), where m is searchWord length and L
is prefix comparison cost.
Space complexity: O(m) for the returned lists, excluding sorting.
*/
