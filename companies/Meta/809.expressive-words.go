package leetcode

// ExpressiveWords809 run-length encodes the target and each word. A word is
// stretchable when group characters match, each word group is no longer than the
// target group, and changed target groups have length at least three.
//
// Time: O(len(s)+total word length). Space: O(groups).
func ExpressiveWords809(s string, words []string) int {
	type group struct {
		ch byte
		n  int
	}
	groups := func(t string) []group {
		res := []group{}
		for i := 0; i < len(t); {
			j := i + 1
			for j < len(t) && t[j] == t[i] {
				j++
			}
			res = append(res, group{t[i], j - i})
			i = j
		}
		return res
	}
	target := groups(s)
	ans := 0
	for _, word := range words {
		g := groups(word)
		if len(g) != len(target) {
			continue
		}
		ok := true
		for i := range target {
			if target[i].ch != g[i].ch || g[i].n > target[i].n || (target[i].n < 3 && g[i].n != target[i].n) {
				ok = false
				break
			}
		}
		if ok {
			ans++
		}
	}
	return ans
}
