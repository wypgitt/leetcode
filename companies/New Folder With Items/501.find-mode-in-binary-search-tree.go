package leetcode

//
// @lc app=leetcode id=501 lang=golang
//
// [501] Find Mode in Binary Search Tree
//
// Notes
// Morris inorder traversal visits a BST in sorted order using O(1) auxiliary
// tree-walk space. Consecutive equal values form a run; track current run length
// and maximum run length, resetting the modes slice when a new maximum appears.
// The temporary threaded links are restored. Time: O(n). Space: O(1) besides
// output.
//
// @lc code=start

func FindMode501(root *TreeNode) []int {
	modes := []int{}
	previousValue := 0
	hasPrevious := false
	currentCount := 0
	maxCount := 0

	visit := func(value int) {
		if hasPrevious && value == previousValue {
			currentCount++
		} else {
			previousValue = value
			hasPrevious = true
			currentCount = 1
		}

		if currentCount > maxCount {
			maxCount = currentCount
			modes = []int{value}
		} else if currentCount == maxCount {
			modes = append(modes, value)
		}
	}

	current := root
	for current != nil {
		if current.Left == nil {
			visit(current.Val)
			current = current.Right
			continue
		}

		predecessor := current.Left
		for predecessor.Right != nil && predecessor.Right != current {
			predecessor = predecessor.Right
		}

		if predecessor.Right == nil {
			predecessor.Right = current
			current = current.Left
		} else {
			predecessor.Right = nil
			visit(current.Val)
			current = current.Right
		}
	}

	return modes
}

// @lc code=end
