package main

func maxAbsValExpr(arr1 []int, arr2 []int) int {
	best := 0
	signs := []int{1, -1}
	for _, sign1 := range signs {
		for _, sign2 := range signs {
			smallest := 1 << 60
			largest := -1 << 60
			for i := range arr1 {
				value := sign1*arr1[i] + sign2*arr2[i] + i
				if value < smallest {
					smallest = value
				}
				if value > largest {
					largest = value
				}
			}
			if largest-smallest > best {
				best = largest - smallest
			}
		}
	}
	return best
}

