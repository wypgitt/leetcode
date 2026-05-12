package main

import "sort"

func shortestDistanceColor(colors []int, queries [][]int) []int {
	positions := map[int][]int{1: []int{}, 2: []int{}, 3: []int{}}
	for index, color := range colors {
		positions[color] = append(positions[color], index)
	}

	answer := make([]int, len(queries))
	for i, query := range queries {
		index, color := query[0], query[1]
		colorPositions := positions[color]
		if len(colorPositions) == 0 {
			answer[i] = -1
			continue
		}

		insertAt := sort.SearchInts(colorPositions, index)
		best := 1 << 30
		if insertAt < len(colorPositions) && colorPositions[insertAt]-index < best {
			best = colorPositions[insertAt] - index
		}
		if insertAt > 0 && index-colorPositions[insertAt-1] < best {
			best = index - colorPositions[insertAt-1]
		}
		answer[i] = best
	}
	return answer
}
