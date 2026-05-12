package main

func maxDepthAfterSplit(seq string) []int {
	answer := make([]int, 0, len(seq))
	depth := 0

	for _, char := range seq {
		if char == '(' {
			depth++
			answer = append(answer, depth&1)
		} else {
			answer = append(answer, depth&1)
			depth--
		}
	}

	return answer
}

