package main

func smallestCommonElement(mat [][]int) int {
	counts := map[int]int{}
	for _, row := range mat {
		for _, value := range row {
			counts[value]++
		}
	}

	for _, value := range mat[0] {
		if counts[value] == len(mat) {
			return value
		}
	}
	return -1
}

