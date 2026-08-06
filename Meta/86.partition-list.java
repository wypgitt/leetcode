/**
 * Algorithm:
 * Build two stable linked lists: nodes with val < x and nodes with val >= x.
 * Append existing nodes to preserve relative order, then connect the lists.
 *
 * Java data structures:
 * Two dummy ListNode heads simplify appending to each partition.
 *
 * Complexity:
 * Time O(n), extra space O(1).
 */
class Solution {
    public ListNode partition(ListNode head, int x) {
        ListNode beforeDummy = new ListNode(0);
        ListNode afterDummy = new ListNode(0);
        ListNode before = beforeDummy;
        ListNode after = afterDummy;
        while (head != null) {
            ListNode next = head.next;
            head.next = null;
            if (head.val < x) {
                before.next = head;
                before = before.next;
            } else {
                after.next = head;
                after = after.next;
            }
            head = next;
        }
        before.next = afterDummy.next;
        return beforeDummy.next;
    }
}

