/**
 * Algorithm:
 * The node to delete is not the tail. Copy the next node's value into this node
 * and bypass the next node.
 *
 * Complexity:
 * Time O(1), space O(1).
 */
class Solution {
    public void deleteNode(ListNode node) {
        node.val = node.next.val;
        node.next = node.next.next;
    }
}

