package main

func sequentialDigits(low int, high int) []int {
	ans := []int{}
	digits := "123456789"

	for length := 2; length <= 9; length++ {
		for start := 0; start+length <= len(digits); start++ {
			num := 0
			for i := start; i < start+length; i++ {
				num = num*10 + int(digits[i]-'0')
			}
			if num >= low && num <= high {
				ans = append(ans, num)
			}
		}
	}

	return ans
}

/*
Explanation

Every sequential-digit number is a contiguous substring of "123456789" with
length at least 2. Generate all such substrings, convert them to integers, and
keep those in the requested range.

There are only 36 candidates, so direct generation is better than scanning
from low to high.

Edge cases: no valid number in range; low/high near one digit; 789 is possible
but 890 is not because digits must be consecutive from 1 to 9.

Time complexity: O(1), fixed candidate count.
Space complexity: O(1) besides output.
*/
