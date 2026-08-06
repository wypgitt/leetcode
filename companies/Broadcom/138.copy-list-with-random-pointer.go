package leetcode

// RandomNode138 is the linked-list node with Random pointer for problem 138.
type RandomNode138 struct {
	Val    int
	Next   *RandomNode138
	Random *RandomNode138
}

// CopyRandomList138 interleaves cloned nodes after originals, sets clone random
// pointers via original.random.next, then detaches the clone list. This keeps O(1)
// auxiliary space beyond the output nodes.
//
// Time: O(n). Space: O(1) auxiliary.
func CopyRandomList138(head *RandomNode138) *RandomNode138 {
	if head == nil {
		return nil
	}
	for cur := head; cur != nil; {
		cur.Next = &RandomNode138{Val: cur.Val, Next: cur.Next}
		cur = cur.Next.Next
	}
	for cur := head; cur != nil; cur = cur.Next.Next {
		if cur.Random != nil {
			cur.Next.Random = cur.Random.Next
		}
	}
	copiedHead := head.Next
	for cur := head; cur != nil; {
		copied := cur.Next
		cur.Next = copied.Next
		cur = cur.Next
		if cur != nil {
			copied.Next = cur.Next
		} else {
			copied.Next = nil
		}
	}
	return copiedHead
}
