/**
 * Algorithm:
 * Split the list in half, reverse the second half, then merge nodes
 * alternately from first and reversed second half.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public void reorderList(ListNode head) {
        if (head == null || head.next == null) {
            return;
        }
        ListNode slow = head;
        ListNode fast = head.next;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        ListNode second = slow.next;
        slow.next = null;

        ListNode prev = null;
        while (second != null) {
            ListNode next = second.next;
            second.next = prev;
            prev = second;
            second = next;
        }

        ListNode first = head;
        second = prev;
        while (second != null) {
            ListNode fnext = first.next;
            ListNode snext = second.next;
            first.next = second;
            second.next = fnext;
            first = fnext;
            second = snext;
        }
    }
}

