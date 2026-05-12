package main

import "strconv"

func encode(num int) string {
	binary := strconv.FormatInt(int64(num+1), 2)
	return binary[1:]
}

/*
Explanation

The encoding for num is the binary representation of num+1 with its leading 1
removed. For example, num=23 gives num+1=24, binary "11000", and encoding
"1000".

Go detail: strconv.FormatInt builds the binary string. Slicing off index 0
removes the leading 1.

Edge case: num=0 gives binary "1", and removing the leading 1 returns the
empty string.

Time complexity: O(log num).
Space complexity: O(log num) for the returned string.
*/
