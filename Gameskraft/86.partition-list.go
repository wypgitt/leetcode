package leetcode

// Partition86 builds two stable lists using existing nodes: values below x and
// values greater/equal x. Detaching each node prevents stale next links before
// the two lists are concatenated.
//
// Time: O(n). Space: O(1).
func Partition86(head *ListNode, x int) *ListNode {
	beforeD, afterD := &ListNode{}, &ListNode{}
	before, after := beforeD, afterD
	for head != nil {
		next := head.Next
		head.Next = nil
		if head.Val < x {
			before.Next = head
			before = before.Next
		} else {
			after.Next = head
			after = after.Next
		}
		head = next
	}
	before.Next = afterD.Next
	return beforeD.Next
}
