package leetcode

// DeleteDuplicates82 removes every duplicated run from a sorted list. A dummy
// node handles duplicate runs at the head; prev stays at the last confirmed
// unique node while cur scans each run.
//
// Time: O(n). Space: O(1).
func DeleteDuplicates82(head *ListNode) *ListNode {
	dummy := &ListNode{Next: head}
	prev := dummy
	cur := head
	for cur != nil {
		dup := false
		for cur.Next != nil && cur.Val == cur.Next.Val {
			dup = true
			cur = cur.Next
		}
		if dup {
			prev.Next = cur.Next
		} else {
			prev = prev.Next
		}
		cur = cur.Next
	}
	return dummy.Next
}
