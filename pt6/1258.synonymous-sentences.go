package main

import "sort"

func generateSentences(synonyms [][]string, text string) []string {
	parent := map[string]string{}

	var find func(string) string
	find = func(word string) string {
		if _, ok := parent[word]; !ok {
			parent[word] = word
		}
		if parent[word] != word {
			parent[word] = find(parent[word])
		}
		return parent[word]
	}

	union := func(a, b string) {
		rootA, rootB := find(a), find(b)
		if rootA != rootB {
			parent[rootB] = rootA
		}
	}

	for _, pair := range synonyms {
		union(pair[0], pair[1])
	}

	groups := map[string][]string{}
	for word := range parent {
		root := find(word)
		groups[root] = append(groups[root], word)
	}

	choices := map[string][]string{}
	for _, words := range groups {
		sort.Strings(words)
		for _, word := range words {
			choices[word] = words
		}
	}

	words := splitWords(text)
	ans := []string{}
	path := make([]string, 0, len(words))

	var backtrack func(int)
	backtrack = func(index int) {
		if index == len(words) {
			ans = append(ans, joinWords(path))
			return
		}
		options, ok := choices[words[index]]
		if !ok {
			options = []string{words[index]}
		}
		for _, option := range options {
			path = append(path, option)
			backtrack(index + 1)
			path = path[:len(path)-1]
		}
	}

	backtrack(0)
	return ans
}

func splitWords(text string) []string {
	words := []string{}
	start := 0
	for i := 0; i <= len(text); i++ {
		if i == len(text) || text[i] == ' ' {
			words = append(words, text[start:i])
			start = i + 1
		}
	}
	return words
}

func joinWords(words []string) string {
	if len(words) == 0 {
		return ""
	}
	total := len(words) - 1
	for _, word := range words {
		total += len(word)
	}
	buf := make([]byte, 0, total)
	for i, word := range words {
		if i > 0 {
			buf = append(buf, ' ')
		}
		buf = append(buf, word...)
	}
	return string(buf)
}

/*
Explanation

Synonyms are transitive, so union-find groups all connected words. After
building components, sort each component. Backtracking over the sentence then
chooses either the sorted synonym list for a word or the word itself when it
has no synonyms.

Union-find is the data structure that turns synonym pairs into connected
components efficiently. Sorting each component ensures generated sentences are
lexicographic because the first differing word decides order.

Go detail: splitWords and joinWords avoid pulling in strings solely for two
simple operations, and joinWords builds the result with a byte buffer.

Edge cases: words without synonyms; synonym chains; duplicate synonym edges.

Time complexity: O(S alpha(W) + R*L), where R is generated sentences and L is
sentence length.
Space complexity: O(W + R*L).
*/
