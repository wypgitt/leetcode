/**
 * Algorithm:
 * Move prev to the node before the sublist, then perform head insertion inside
 * the sublist: repeatedly remove cur.next and insert it after prev.
 *
 * Java data structures:
 * A dummy ListNode handles reversal starting at the original head.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public ListNode reverseBetween(ListNode head, int left, int right) {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;
        for (int i = 0; i < left - 1; i++) {
            prev = prev.next;
        }
        ListNode cur = prev.next;
        for (int i = 0; i < right - left; i++) {
            ListNode move = cur.next;
            cur.next = move.next;
            move.next = prev.next;
            prev.next = move;
        }
        return dummy.next;
    }
}

