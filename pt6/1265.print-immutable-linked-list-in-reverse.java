/*
interface ImmutableListNode {
    void printValue();
    ImmutableListNode getNext();
}
*/

class Solution {
    public void printLinkedListInReverse(ImmutableListNode head) {
        if (head == null) {
            return;
        }
        printLinkedListInReverse(head.getNext());
        head.printValue();
    }
}

/*
Explanation

The linked list is immutable and singly linked, so we cannot reverse pointers.
Recursion walks to the tail first, then prints while the call stack unwinds.
The call stack stores the nodes in forward order and releases them in reverse.

This uses only the provided Java API: getNext and printValue.

Edge cases: null head prints nothing; a one-node list prints after the recursive
call on null.

Time complexity: O(n).
Space complexity: O(n) recursion stack.
*/
