package leetcode

// ReorderList143 splits the list in half, reverses the second half, then merges
// nodes alternately from first and reversed second halves to form L0,Ln,L1,...
// in place.
//
// Time: O(n). Space: O(1).
func ReorderList143(head *ListNode) {
	if head == nil || head.Next == nil {
		return
	}
	slow, fast := head, head.Next
	for fast != nil && fast.Next != nil {
		slow = slow.Next
		fast = fast.Next.Next
	}
	second := slow.Next
	slow.Next = nil
	var prev *ListNode
	for second != nil {
		nxt := second.Next
		second.Next = prev
		prev = second
		second = nxt
	}
	first := head
	second = prev
	for second != nil {
		fnext, snext := first.Next, second.Next
		first.Next = second
		second.Next = fnext
		first, second = fnext, snext
	}
}
