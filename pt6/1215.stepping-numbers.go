package main

import "sort"

func countSteppingNumbers(low int, high int) []int {
	ans := []int{}
	queue := make([]int, 10)
	for i := 0; i < 10; i++ {
		queue[i] = i
	}

	for head := 0; head < len(queue); head++ {
		num := queue[head]
		if num > high {
			continue
		}
		if num >= low {
			ans = append(ans, num)
		}
		if num == 0 {
			continue
		}

		last := num % 10
		if last > 0 {
			queue = append(queue, num*10+last-1)
		}
		if last < 9 {
			queue = append(queue, num*10+last+1)
		}
	}

	sort.Ints(ans)
	return ans
}

/*
Explanation

A stepping number can be grown from its last digit. If the last digit is d, the
next digit can only be d-1 or d+1. Start a BFS queue with 0 through 9 and append
valid next numbers.

The queue stores only valid stepping-number prefixes, so we never scan the
entire numeric range. Zero is reported if it is in range, but it is not
extended; otherwise we would create leading-zero numbers like 01.

Go detail: the queue is a slice with a head index, avoiding O(n) front removals.
The final sort gives increasing order because BFS from multiple roots can
produce values in mixed order.

Edge cases: ranges including 0; high < 10; last digit 0 or 9 has only one
possible extension.

Time complexity: O(k log k), where k is the number of generated answers.
Space complexity: O(k).
*/
