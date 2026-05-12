package main

func groupThePeople(groupSizes []int) [][]int {
	buckets := map[int][]int{}
	ans := [][]int{}

	for person, size := range groupSizes {
		buckets[size] = append(buckets[size], person)
		if len(buckets[size]) == size {
			ans = append(ans, buckets[size])
			buckets[size] = nil
		}
	}

	return ans
}

/*
Explanation

Bucket people by required group size. Whenever a bucket reaches that size, it
forms a complete group and is flushed to the answer.

A hash map from size to current partial group is enough because people with the
same group size are interchangeable. The problem guarantees that a valid
partition exists.

Edge cases: size 1 groups flush immediately; many groups can share one size;
the output order can be any valid order.

Time complexity: O(n).
Space complexity: O(n).
*/
