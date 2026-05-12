package main

import "sort"

func minimumCost(n int, connections [][]int) int {
	if n == 1 {
		return 0
	}

	parent := make([]int, n+1)
	rank := make([]int, n+1)
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

	union := func(a, b int) bool {
		rootA, rootB := find(a), find(b)
		if rootA == rootB {
			return false
		}
		if rank[rootA] < rank[rootB] {
			rootA, rootB = rootB, rootA
		}
		parent[rootB] = rootA
		if rank[rootA] == rank[rootB] {
			rank[rootA]++
		}
		return true
	}

	sort.Slice(connections, func(i, j int) bool {
		return connections[i][2] < connections[j][2]
	})

	total, used := 0, 0
	for _, edge := range connections {
		if union(edge[0], edge[1]) {
			total += edge[2]
			used++
			if used == n-1 {
				return total
			}
		}
	}
	return -1
}

