/**
 * Algorithm:
 * Build a sorted linked list by inserting each original node into its correct
 * position after a dummy head. This is direct insertion sort on linked nodes.
 *
 * Complexity:
 * Time O(n^2), space O(1).
 */
class Solution {
    public ListNode insertionSortList(ListNode head) {
        ListNode dummy = new ListNode(0);
        ListNode cur = head;
        while (cur != null) {
            ListNode next = cur.next;
            ListNode prev = dummy;
            while (prev.next != null && prev.next.val < cur.val) {
                prev = prev.next;
            }
            cur.next = prev.next;
            prev.next = cur;
            cur = next;
        }
        return dummy.next;
    }
}

