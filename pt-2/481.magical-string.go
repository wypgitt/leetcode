package leetcode

// MagicalString481 generates the self-describing run-length string from the
// seed 122. The read pointer supplies the next run length; nextValue alternates
// between 1 and 2. Ones are counted only until length n is reached.
//
// Go data structure note: []int is a growable slice because generated values
// become future run lengths.
//
// Time: O(n). Space: O(n).
func MagicalString481(n int) int {
	if n <= 0 {
		return 0
	}
	s := []int{1, 2, 2}
	if n <= 3 {
		ans := 0
		for i := 0; i < n; i++ {
			if s[i] == 1 {
				ans++
			}
		}
		return ans
	}
	read, nextNum, ones := 2, 1, 1
	for len(s) < n {
		repeat := s[read]
		for i := 0; i < repeat && len(s) < n; i++ {
			s = append(s, nextNum)
			if nextNum == 1 {
				ones++
			}
		}
		nextNum = 3 - nextNum
		read++
	}
	return ones
}
