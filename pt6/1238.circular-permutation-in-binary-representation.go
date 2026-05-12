package main

func circularPermutation(n int, start int) []int {
	size := 1 << n
	ans := make([]int, size)
	for i := 0; i < size; i++ {
		gray := i ^ (i >> 1)
		ans[i] = start ^ gray
	}
	return ans
}

/*
Explanation

i ^ (i >> 1) generates the standard n-bit Gray code sequence: adjacent values
differ by one bit, and the last also differs from the first by one bit. XOR
every value with start. XOR is a bijection and preserves bit differences, so
the sequence remains circular and now begins with start.

This direct construction is simpler and faster than backtracking over the
hypercube.

Edge cases: n == 1 returns two numbers; start can be any n-bit value.

Time complexity: O(2^n).
Space complexity: O(2^n) for the returned slice.
*/
