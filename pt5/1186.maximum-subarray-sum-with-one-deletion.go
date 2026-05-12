package main

func maximumSum(arr []int) int {
	noDelete := arr[0]
	oneDelete := -1 << 60
	best := arr[0]

	for i := 1; i < len(arr); i++ {
		value := arr[i]
		if noDelete > oneDelete+value {
			oneDelete = noDelete
		} else {
			oneDelete = oneDelete + value
		}

		if noDelete+value > value {
			noDelete = noDelete + value
		} else {
			noDelete = value
		}

		if noDelete > best {
			best = noDelete
		}
		if oneDelete > best {
			best = oneDelete
		}
	}
	return best
}

