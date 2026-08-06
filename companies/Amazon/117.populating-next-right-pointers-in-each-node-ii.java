/*
 * LeetCode provides:
 * class Node {
 *     public int val;
 *     public Node left;
 *     public Node right;
 *     public Node next;
 * }
 */

/**
 * Algorithm:
 * The tree is not perfect, so build the next level while walking the current
 * one through next pointers. A dummy head and tail append existing children in
 * left-to-right order.
 *
 * Java data structures:
 * A temporary dummy Node is a constant-space linked-list builder for the next
 * level.
 *
 * Complexity:
 * Time O(n), extra space O(1).
 */
class Solution {
    public Node connect(Node root) {
        Node current = root;
        while (current != null) {
            Node dummy = new Node(0);
            Node tail = dummy;
            while (current != null) {
                if (current.left != null) {
                    tail.next = current.left;
                    tail = tail.next;
                }
                if (current.right != null) {
                    tail.next = current.right;
                    tail = tail.next;
                }
                current = current.next;
            }
            current = dummy.next;
        }
        return root;
    }
}

