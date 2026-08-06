package leetcode

// GroupAnagrams49 uses a [26]int character-count array as the map key. This is
// a Go-specific advantage: fixed arrays are comparable, so they can be map keys
// without converting to strings or sorting each word.
//
// Time: O(total characters). Space: O(number of groups * 26) plus output.
func GroupAnagrams49(strs []string) [][]string {
	groups := map[[26]int][]string{}
	for _, w := range strs {
		var key [26]int
		for i := 0; i < len(w); i++ {
			key[w[i]-'a']++
		}
		groups[key] = append(groups[key], w)
	}
	ans := [][]string{}
	for _, g := range groups {
		ans = append(ans, g)
	}
	return ans
}
