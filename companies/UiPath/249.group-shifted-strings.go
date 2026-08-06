package leetcode

import (
	"strconv"
	"strings"
)

// GroupStrings249 normalizes each string by its cyclic offsets from the first
// character. Shift-equivalent strings share that key and are grouped together.
//
// Time: O(total characters). Space: O(total characters).
func GroupStrings249(stringsIn []string) [][]string {
	groups := map[string][]string{}
	for _, s := range stringsIn {
		parts := make([]string, len(s))
		base := s[0]
		for i := 0; i < len(s); i++ {
			parts[i] = strconv.Itoa((int(s[i]) - int(base) + 26) % 26)
		}
		key := strings.Join(parts, "#")
		groups[key] = append(groups[key], s)
	}
	ans := [][]string{}
	for _, g := range groups {
		ans = append(ans, g)
	}
	return ans
}
