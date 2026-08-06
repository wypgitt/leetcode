package leetcode

//
// @lc app=leetcode id=382 lang=golang
//
// [382] Linked List Random Node
//
// Notes
// Reservoir sampling chooses one node uniformly without knowing list length in
// advance. When visiting the i-th node, replace the current choice with
// probability 1/i. Go's math/rand.Intn supplies the random draw; the list node
// type is the shared ListNode from leetcode_common_types.go. Time per call:
// O(n). Space: O(1).
//
// @lc code=start

import "math/rand"

type RandomNode382 struct {
	head *ListNode
}

func NewRandomNode382(head *ListNode) *RandomNode382 {
	return &RandomNode382{head: head}
}

func (r *RandomNode382) GetRandom() int {
	current := r.head
	nodesSeen := 0
	chosenValue := 0
	for current != nil {
		nodesSeen++
		if rand.Intn(nodesSeen) == 0 {
			chosenValue = current.Val
		}
		current = current.Next
	}
	return chosenValue
}

// @lc code=end
