package leetcode

// DeleteNode237 deletes a non-tail node when only that node pointer is given by
// copying the next node's value and bypassing the next node.
//
// Time: O(1). Space: O(1).
func DeleteNode237(node *ListNode) { node.Val = node.Next.Val; node.Next = node.Next.Next }
