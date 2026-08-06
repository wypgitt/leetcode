package leetcode

import "strings"

// RestoreIpAddresses93 backtracks over exactly four segments, each length 1..3,
// value <=255, and no leading zero unless the segment is "0". Remaining length
// pruning keeps the search bounded.
//
// Time/space: O(1) in practice because at most 3^4 segment choices exist.
func RestoreIpAddresses93(s string) []string {
	ans := []string{}
	path := []string{}
	valid := func(part string) bool {
		if len(part) > 1 && part[0] == '0' {
			return false
		}
		v := 0
		for i := 0; i < len(part); i++ {
			v = v*10 + int(part[i]-'0')
		}
		return v <= 255
	}
	var dfs func(int)
	dfs = func(idx int) {
		partsLeft := 4 - len(path)
		charsLeft := len(s) - idx
		if charsLeft < partsLeft || charsLeft > partsLeft*3 {
			return
		}
		if len(path) == 4 {
			if idx == len(s) {
				ans = append(ans, strings.Join(path, "."))
			}
			return
		}
		for end := idx + 1; end <= idx+3 && end <= len(s); end++ {
			part := s[idx:end]
			if valid(part) {
				path = append(path, part)
				dfs(end)
				path = path[:len(path)-1]
			}
		}
	}
	dfs(0)
	return ans
}
