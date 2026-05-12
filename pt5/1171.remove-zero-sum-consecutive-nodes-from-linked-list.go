package main

type ListNode struct {
	Val  int
	Next *ListNode
}

func removeZeroSumSublists(head *ListNode) *ListNode {
	dummy := &ListNode{Next: head}
	prefixToNode := map[int]*ListNode{}
	prefix := 0

	for node := dummy; node != nil; node = node.Next {
		prefix += node.Val
		prefixToNode[prefix] = node
	}

	prefix = 0
	for node := dummy; node != nil; node = node.Next {
		prefix += node.Val
		node.Next = prefixToNode[prefix].Next
	}

	return dummy.Next
}

