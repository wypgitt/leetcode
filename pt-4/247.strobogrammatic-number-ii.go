package leetcode

// FindStrobogrammatic247 builds numbers from the outside inward using valid
// rotated digit pairs. The outermost layer skips 0 unless the total length is 1.
//
// Time/space: proportional to output size.
func FindStrobogrammatic247(n int) []string {
	pairs := [][2]string{{"0", "0"}, {"1", "1"}, {"6", "9"}, {"8", "8"}, {"9", "6"}}
	var build func(int, int) []string
	build = func(length, total int) []string {
		if length == 0 {
			return []string{""}
		}
		if length == 1 {
			return []string{"0", "1", "8"}
		}
		ans := []string{}
		for _, inner := range build(length-2, total) {
			for _, p := range pairs {
				if length == total && p[0] == "0" {
					continue
				}
				ans = append(ans, p[0]+inner+p[1])
			}
		}
		return ans
	}
	return build(n, n)
}
