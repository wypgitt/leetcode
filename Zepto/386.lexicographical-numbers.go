package leetcode

// LexicalOrder386 traverses the implicit decimal prefix tree in preorder.
// From x, descend to x*10 when possible; otherwise climb until a next sibling
// exists and move to x+1.
//
// Go data structure note: no trie is allocated; integer arithmetic navigates the
// implicit tree and a slice stores the required output.
//
// Time: O(n) amortized. Extra space: O(1), excluding the O(n) answer slice.
func LexicalOrder386(n int) []int {
	ans := make([]int, 0, n)
	cur := 1
	for i := 0; i < n; i++ {
		ans = append(ans, cur)
		if cur*10 <= n {
			cur *= 10
		} else {
			for cur%10 == 9 || cur+1 > n {
				cur /= 10
			}
			cur++
		}
	}
	return ans
}
