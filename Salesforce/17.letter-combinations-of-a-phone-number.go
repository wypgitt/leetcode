package leetcode

// LetterCombinations17 backtracks through the Cartesian product of letters for
// each digit. A byte path is reused during recursion and copied into a string at
// each leaf.
//
// Time: O(4^n*n). Space: O(n) recursion excluding output.
func LetterCombinations17(digits string) []string {
	if digits == "" {
		return []string{}
	}
	phone := map[byte]string{'2': "abc", '3': "def", '4': "ghi", '5': "jkl", '6': "mno", '7': "pqrs", '8': "tuv", '9': "wxyz"}
	ans := []string{}
	path := []byte{}
	var dfs func(int)
	dfs = func(idx int) {
		if idx == len(digits) {
			ans = append(ans, string(path))
			return
		}
		for i := 0; i < len(phone[digits[idx]]); i++ {
			path = append(path, phone[digits[idx]][i])
			dfs(idx + 1)
			path = path[:len(path)-1]
		}
	}
	dfs(0)
	return ans
}
