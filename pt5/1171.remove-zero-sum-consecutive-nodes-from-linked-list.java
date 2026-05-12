import java.util.*;

class ListNode {
    int val;
    ListNode next;

    ListNode() {}

    ListNode(int val) {
        this.val = val;
    }

    ListNode(int val, ListNode next) {
        this.val = val;
        this.next = next;
    }
}

class Solution {
    public ListNode removeZeroSumSublists(ListNode head) {
        ListNode dummy = new ListNode(0, head);
        Map<Integer, ListNode> prefixToNode = new HashMap<>();
        int prefix = 0;

        for (ListNode node = dummy; node != null; node = node.next) {
            prefix += node.val;
            prefixToNode.put(prefix, node);
        }

        prefix = 0;
        for (ListNode node = dummy; node != null; node = node.next) {
            prefix += node.val;
            node.next = prefixToNode.get(prefix).next;
        }

        return dummy.next;
    }
}

