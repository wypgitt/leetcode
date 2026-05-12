package main

import (
	"sort"
	"strings"
)

func removeSubfolders(folder []string) []string {
	sort.Strings(folder)
	roots := []string{}

	for _, path := range folder {
		if len(roots) == 0 || !strings.HasPrefix(path, roots[len(roots)-1]+"/") {
			roots = append(roots, path)
		}
	}

	return roots
}

/*
Explanation

Sort folders lexicographically. A parent appears before all of its subfolders,
so we only need to compare each path with the latest accepted root. A path is a
subfolder exactly when it starts with root + "/".

The slash matters: "/a/b" is under "/a", but "/ab" is not. Sorting removes the
need for a trie because descendants are grouped directly after their parent.

Edge cases: sibling folders with common prefixes; deep chains like /a/b/c;
empty result is impossible because each path itself can be a root.

Time complexity: O(n log n * L) for sorting and prefix comparisons.
Space complexity: O(n) for the result.
*/
