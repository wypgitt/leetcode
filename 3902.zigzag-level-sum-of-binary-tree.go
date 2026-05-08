package leetcode

//
// @lc app=leetcode id=3902 lang=golang
//
// [3902] Zigzag Level Sum of Binary Tree
//
// Notes
// Traverse the tree level by level. Odd levels scan left-to-right and stop at
// the first node without a left child; even levels scan right-to-left and stop
// at the first node without a right child. Children for the next level are still
// collected in normal order. Time: O(n). Space: O(width).
//
// @lc code=start

func ZigzagLevelSum3902(root *TreeNode) []int {
	if root == nil {
		return []int{}
	}

	answer := []int{}
	current := []*TreeNode{root}
	level := 1

	for len(current) > 0 {
		nextLevel := []*TreeNode{}
		for _, node := range current {
			if node.Left != nil {
				nextLevel = append(nextLevel, node.Left)
			}
			if node.Right != nil {
				nextLevel = append(nextLevel, node.Right)
			}
		}

		levelSum := 0
		if level%2 == 1 {
			for _, node := range current {
				if node.Left == nil {
					break
				}
				levelSum += node.Val
			}
		} else {
			for i := len(current) - 1; i >= 0; i-- {
				node := current[i]
				if node.Right == nil {
					break
				}
				levelSum += node.Val
			}
		}

		answer = append(answer, levelSum)
		current = nextLevel
		level++
	}

	return answer
}

// @lc code=end
