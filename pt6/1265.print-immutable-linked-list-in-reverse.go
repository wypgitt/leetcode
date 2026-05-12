package main

type ImmutableListNode interface {
	printValue()
	getNext() ImmutableListNode
}

func printLinkedListInReverse(head ImmutableListNode) {
	if head == nil {
		return
	}
	printLinkedListInReverse(head.getNext())
	head.printValue()
}

/*
Explanation

The list is immutable and singly linked, so we cannot reverse pointers. Use
recursion to walk to the tail first, then print while the call stack unwinds.
The call stack stores the nodes in forward order and releases them in reverse.

This solution uses only the provided API: getNext and printValue.

Edge cases: nil head prints nothing; one node prints after the recursive call
on nil.

Time complexity: O(n).
Space complexity: O(n) recursion stack. A stricter-memory follow-up can use
block decomposition, but recursion is the direct interview solution.
*/
