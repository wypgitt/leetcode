/**
 * Algorithm:
 * Interleave copied nodes after originals, wire copied random pointers via
 * original.random.next, then detach the copied list while restoring originals.
 *
 * Java data structures:
 * The list itself stores the temporary original->copy mapping, so no HashMap is
 * needed.
 *
 * Complexity:
 * Time O(n), extra space O(1) excluding copied nodes.
 */
class Solution {
    public Node copyRandomList(Node head) {
        if (head == null) {
            return null;
        }
        Node cur = head;
        while (cur != null) {
            Node copied = new Node(cur.val);
            copied.next = cur.next;
            cur.next = copied;
            cur = copied.next;
        }
        cur = head;
        while (cur != null) {
            if (cur.random != null) {
                cur.next.random = cur.random.next;
            }
            cur = cur.next.next;
        }
        cur = head;
        Node copiedHead = head.next;
        while (cur != null) {
            Node copied = cur.next;
            cur.next = copied.next;
            cur = cur.next;
            copied.next = cur == null ? null : cur.next;
        }
        return copiedHead;
    }
}

