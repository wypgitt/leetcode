package leetcode

// InsertionSortList147 inserts each original node into a new sorted list headed
// by a dummy node. The list is singly linked, so each insertion scans from dummy
// to find the first node with value >= current.
//
// Time: O(n^2). Space: O(1).
func InsertionSortList147(head *ListNode) *ListNode {
	dummy := &ListNode{}
	for cur := head; cur != nil; {
		nxt := cur.Next
		prev := dummy
		for prev.Next != nil && prev.Next.Val < cur.Val {
			prev = prev.Next
		}
		cur.Next = prev.Next
		prev.Next = cur
		cur = nxt
	}
	return dummy.Next
}
