package main

func mctFromLeafValues(arr []int) int {
	const inf = int(^uint(0) >> 1)
	stack := []int{inf}
	cost := 0

	for _, value := range arr {
		for stack[len(stack)-1] <= value {
			middle := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			left := stack[len(stack)-1]
			if value < left {
				cost += middle * value
			} else {
				cost += middle * left
			}
		}
		stack = append(stack, value)
	}

	for len(stack) > 2 {
		last := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		cost += last * stack[len(stack)-1]
	}

	return cost
}

