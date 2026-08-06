/**
 * Algorithm:
 * The lists store least-significant digits first, so walk both lists from head
 * to tail, adding digits plus carry exactly like elementary addition. Append
 * each result digit to a new list.
 *
 * Java data structures:
 * A dummy head simplifies appending to the result linked list.
 *
 * Complexity:
 * Time O(max(m, n)), output space O(max(m, n)).
 */
class Solution {
    public ListNode addTwoNumbers(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        int carry = 0;
        while (l1 != null || l2 != null || carry != 0) {
            int total = carry;
            if (l1 != null) {
                total += l1.val;
                l1 = l1.next;
            }
            if (l2 != null) {
                total += l2.val;
                l2 = l2.next;
            }
            carry = total / 10;
            tail.next = new ListNode(total % 10);
            tail = tail.next;
        }
        return dummy.next;
    }
}

