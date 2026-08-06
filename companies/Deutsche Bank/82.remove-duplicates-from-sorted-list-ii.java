/**
 * Algorithm:
 * Since the list is sorted, duplicates occur in consecutive runs. A dummy node
 * handles duplicated runs at the head. prev points to the last confirmed unique
 * node; cur scans each run and either keeps or removes it.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public ListNode deleteDuplicates(ListNode head) {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;
        ListNode cur = head;
        while (cur != null) {
            boolean duplicate = false;
            while (cur.next != null && cur.val == cur.next.val) {
                duplicate = true;
                cur = cur.next;
            }
            if (duplicate) {
                prev.next = cur.next;
            } else {
                prev = prev.next;
            }
            cur = cur.next;
        }
        return dummy.next;
    }
}

