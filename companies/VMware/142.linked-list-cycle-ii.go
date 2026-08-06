package leetcode

// DetectCycle142 uses Floyd's slow/fast pointers. After the meeting point, a
// pointer from head and one from the meeting point move together; their meeting
// point is the cycle entry.
//
// Time: O(n). Space: O(1).
func DetectCycle142(head *ListNode) *ListNode {
	slow, fast := head, head
	for fast != nil && fast.Next != nil {
		slow = slow.Next
		fast = fast.Next.Next
		if slow == fast {
			finder := head
			for finder != slow {
				finder = finder.Next
				slow = slow.Next
			}
			return finder
		}
	}
	return nil
}
