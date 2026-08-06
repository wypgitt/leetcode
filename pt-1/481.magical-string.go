package leetcode

//
// @lc app=leetcode id=481 lang=golang
//
// [481] Magical String
//
// Notes
// Generate the magical string from its run-length description. The read pointer
// tells how many copies of the next value to append; nextValue alternates
// between 1 and 2. Count appended ones only while the generated length is within
// n. Time: O(n). Space: O(n).
//
// @lc code=start

func MagicalString481(n int) int {
	if n <= 3 {
		return 1
	}

	magical := []int{1, 2, 2}
	read := 2
	nextValue := 1
	ones := 1

	for len(magical) < n {
		repeat := magical[read]
		for i := 0; i < repeat; i++ {
			magical = append(magical, nextValue)
			if nextValue == 1 && len(magical) <= n {
				ones++
			}
		}
		nextValue = 3 - nextValue
		read++
	}

	return ones
}

// @lc code=end
