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
 * In a perfect binary tree, every internal node has both children. Walk each
 * level using already-created next pointers, linking node.left -> node.right
 * and node.right -> node.next.left when a neighbor exists.
 *
 * Java data structures:
 * No queue is needed; next pointers act as the level traversal structure.
 *
 * Complexity:
 * Time O(n), extra space O(1).
 */
class Solution {
    public Node connect(Node root) {
        Node leftmost = root;
        while (leftmost != null && leftmost.left != null) {
            Node node = leftmost;
            while (node != null) {
                node.left.next = node.right;
                if (node.next != null) {
                    node.right.next = node.next.left;
                }
                node = node.next;
            }
            leftmost = leftmost.left;
        }
        return root;
    }
}

