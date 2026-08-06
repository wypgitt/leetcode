package leetcode

// ReverseBetween92 reverses [left,right] in place with head insertion. prev is
// the node before the segment; repeatedly moving cur.Next after prev reverses the
// segment without extra nodes.
//
// Time: O(n). Space: O(1).
func ReverseBetween92(head *ListNode, left int, right int) *ListNode {
	dummy := &ListNode{Next: head}
	prev := dummy
	for i := 0; i < left-1; i++ {
		prev = prev.Next
	}
	cur := prev.Next
	for i := 0; i < right-left; i++ {
		move := cur.Next
		cur.Next = move.Next
		move.Next = prev.Next
		prev.Next = move
	}
	return dummy.Next
}
