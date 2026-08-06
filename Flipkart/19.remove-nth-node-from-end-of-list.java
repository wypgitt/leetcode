/**
 * Algorithm:
 * Keep fast n nodes ahead of slow. Starting both at a dummy node means removing
 * the original head is the same pointer operation as any other deletion.
 *
 * Complexity:
 * Time O(L), space O(1).
 */
class Solution {
    public ListNode removeNthFromEnd(ListNode head, int n) {
        ListNode dummy = new ListNode(0, head);
        ListNode fast = dummy;
        ListNode slow = dummy;
        for (int i = 0; i < n; i++) {
            fast = fast.next;
        }
        while (fast.next != null) {
            fast = fast.next;
            slow = slow.next;
        }
        slow.next = slow.next.next;
        return dummy.next;
    }
}

