package leetcode

// RotateRight61 computes length, links tail to head to form a cycle, then breaks
// the cycle at the new tail. The new head is length-k%length nodes from the old
// head.
//
// Time: O(n). Space: O(1).
func RotateRight61(head *ListNode, k int) *ListNode {
	if head == nil || head.Next == nil || k == 0 {
		return head
	}
	length := 1
	tail := head
	for tail.Next != nil {
		tail = tail.Next
		length++
	}
	k %= length
	if k == 0 {
		return head
	}
	tail.Next = head
	steps := length - k - 1
	newTail := head
	for i := 0; i < steps; i++ {
		newTail = newTail.Next
	}
	newHead := newTail.Next
	newTail.Next = nil
	return newHead
}
