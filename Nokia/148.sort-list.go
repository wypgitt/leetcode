package leetcode

// SortList148 performs merge sort on a linked list: split by slow/fast pointers,
// recursively sort halves, then merge sorted lists. This gives O(n log n) without
// converting to an array.
//
// Time: O(n log n). Space: O(log n) recursion.
func SortList148(head *ListNode) *ListNode {
	if head == nil || head.Next == nil {
		return head
	}
	slow, fast := head, head.Next
	for fast != nil && fast.Next != nil {
		slow = slow.Next
		fast = fast.Next.Next
	}
	second := slow.Next
	slow.Next = nil
	return mergeList148(SortList148(head), SortList148(second))
}
func mergeList148(a, b *ListNode) *ListNode {
	dummy := &ListNode{}
	tail := dummy
	for a != nil && b != nil {
		if a.Val <= b.Val {
			tail.Next = a
			a = a.Next
		} else {
			tail.Next = b
			b = b.Next
		}
		tail = tail.Next
	}
	if a != nil {
		tail.Next = a
	} else {
		tail.Next = b
	}
	return dummy.Next
}
