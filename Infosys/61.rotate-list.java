/**
 * Algorithm:
 * Compute length, connect tail to head to form a cycle, then break the cycle at
 * the new tail. Rotating right by k makes the length - k % length node the new
 * head.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public ListNode rotateRight(ListNode head, int k) {
        if (head == null || head.next == null || k == 0) {
            return head;
        }
        int length = 1;
        ListNode tail = head;
        while (tail.next != null) {
            tail = tail.next;
            length++;
        }
        k %= length;
        if (k == 0) {
            return head;
        }
        tail.next = head;
        int stepsToNewTail = length - k - 1;
        ListNode newTail = head;
        for (int i = 0; i < stepsToNewTail; i++) {
            newTail = newTail.next;
        }
        ListNode newHead = newTail.next;
        newTail.next = null;
        return newHead;
    }
}

