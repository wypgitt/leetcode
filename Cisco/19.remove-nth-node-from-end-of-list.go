package leetcode

// RemoveNthFromEnd19 keeps a gap of n nodes between fast and slow. The dummy
// predecessor makes removing the original head the same operation as any other
// deletion.
//
// Time: O(L). Space: O(1).
func RemoveNthFromEnd19(head *ListNode, n int) *ListNode {
	dummy := &ListNode{Next: head}
	fast, slow := dummy, dummy
	for i := 0; i < n; i++ {
		fast = fast.Next
	}
	for fast.Next != nil {
		fast = fast.Next
		slow = slow.Next
	}
	slow.Next = slow.Next.Next
	return dummy.Next
}
