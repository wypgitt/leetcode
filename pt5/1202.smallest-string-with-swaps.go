package main

import "sort"

func smallestStringWithSwaps(s string, pairs [][]int) string {
	parent := make([]int, len(s))
	rank := make([]int, len(s))
	for i := range parent {
		parent[i] = i
	}

	var find func(int) int
	find = func(x int) int {
		if parent[x] != x {
			parent[x] = find(parent[x])
		}
		return parent[x]
	}

	union := func(a, b int) {
		rootA, rootB := find(a), find(b)
		if rootA == rootB {
			return
		}
		if rank[rootA] < rank[rootB] {
			rootA, rootB = rootB, rootA
		}
		parent[rootB] = rootA
		if rank[rootA] == rank[rootB] {
			rank[rootA]++
		}
	}

	for _, pair := range pairs {
		union(pair[0], pair[1])
	}

	groups := map[int][]byte{}
	for i := 0; i < len(s); i++ {
		root := find(i)
		groups[root] = append(groups[root], s[i])
	}

	for root := range groups {
		sort.Slice(groups[root], func(i, j int) bool {
			return groups[root][i] > groups[root][j]
		})
	}

	answer := make([]byte, len(s))
	for i := range answer {
		root := find(i)
		chars := groups[root]
		answer[i] = chars[len(chars)-1]
		groups[root] = chars[:len(chars)-1]
	}
	return string(answer)
}

