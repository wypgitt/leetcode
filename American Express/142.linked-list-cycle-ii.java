/**
 * Algorithm:
 * Floyd cycle detection. After slow and fast meet, move one pointer from head
 * and one from the meeting point; their next meeting is the cycle entry.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public ListNode detectCycle(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {
                ListNode finder = head;
                while (finder != slow) {
                    finder = finder.next;
                    slow = slow.next;
                }
                return finder;
            }
        }
        return null;
    }
}

