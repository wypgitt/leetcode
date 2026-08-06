package leetcode

// SwapPairs24 rewires nodes pair by pair using a dummy predecessor. For each
// pair first->second, reconnect prev->second->first->nextPair without swapping
// values.
//
// Time: O(n). Space: O(1).
func SwapPairs24(head *ListNode) *ListNode {
	dummy := &ListNode{Next: head}
	prev := dummy
	for prev.Next != nil && prev.Next.Next != nil {
		first := prev.Next
		second := first.Next
		first.Next = second.Next
		second.Next = first
		prev.Next = second
		prev = first
	}
	return dummy.Next
}
