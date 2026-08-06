package leetcode

// AddTwoNumbers2 simulates elementary addition over reversed digit lists. A
// dummy head lets Go append result nodes uniformly without special-casing the
// first digit. Different list lengths and a final carry are handled in the same
// loop.
//
// Time: O(max(m,n)). Space: O(max(m,n)) for the output list.
func AddTwoNumbers2(l1 *ListNode, l2 *ListNode) *ListNode {
	dummy := &ListNode{}
	tail := dummy
	carry := 0
	for l1 != nil || l2 != nil || carry != 0 {
		total := carry
		if l1 != nil {
			total += l1.Val
			l1 = l1.Next
		}
		if l2 != nil {
			total += l2.Val
			l2 = l2.Next
		}
		carry = total / 10
		tail.Next = &ListNode{Val: total % 10}
		tail = tail.Next
	}
	return dummy.Next
}
