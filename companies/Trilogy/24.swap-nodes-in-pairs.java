/**
 * Algorithm:
 * Rewire pointers in pairs using a dummy predecessor. For pair first -> second,
 * reconnect prev -> second -> first -> nextPair.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public ListNode swapPairs(ListNode head) {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;
        while (prev.next != null && prev.next.next != null) {
            ListNode first = prev.next;
            ListNode second = first.next;
            first.next = second.next;
            second.next = first;
            prev.next = second;
            prev = first;
        }
        return dummy.next;
    }
}

