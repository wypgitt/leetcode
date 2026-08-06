/*
 * @lc app=leetcode id=382 lang=java
 *
 * [382] Linked List Random Node
 *
 * Reservoir sampling over a singly linked list. After seeing t nodes, replace
 * the chosen value with probability 1/t. Therefore every node is selected with
 * equal probability without knowing the list length in advance.
 *
 * Java note: java.util.Random.nextInt(t) returns a uniform integer in [0, t).
 *
 * Time per getRandom: O(n). Space: O(1).
 */

import java.util.Random;

// @lc code=start
/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    private final ListNode head;
    private final Random random = new Random();

    public Solution(ListNode head) {
        this.head = head;
    }

    public int getRandom() {
        ListNode current = head;
        int seen = 0;
        int chosen = 0;

        while (current != null) {
            seen++;
            if (random.nextInt(seen) == 0) {
                chosen = current.val;
            }
            current = current.next;
        }
        return chosen;
    }
}
// @lc code=end
