package main

import "math/bits"

func pathInZigZagTree(label int) []int {
	path := []int{}
	for label > 0 {
		path = append(path, label)
		levelStart := 1 << (bits.Len(uint(label)) - 1)
		levelEnd := (levelStart << 1) - 1
		label = (levelStart + levelEnd - label) / 2
	}

	for left, right := 0, len(path)-1; left < right; left, right = left+1, right-1 {
		path[left], path[right] = path[right], path[left]
	}
	return path
}

