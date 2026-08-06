package leetcode

// VerifyPreorder255 simulates the path stack of BST preorder traversal. Popping
// while value is greater means we moved into a right subtree; the popped value
// becomes a lower bound that future values must exceed.
//
// Time: O(n). Space: O(n).
func VerifyPreorder255(preorder []int) bool {
	stack := []int{}
	lower := -1 << 63
	for _, v := range preorder {
		if v < lower {
			return false
		}
		for len(stack) > 0 && v > stack[len(stack)-1] {
			lower = stack[len(stack)-1]
			stack = stack[:len(stack)-1]
		}
		stack = append(stack, v)
	}
	return true
}
