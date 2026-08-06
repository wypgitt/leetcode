/*
 * @lc app=leetcode id=919 lang=java
 *
 * [919] Complete Binary Tree Inserter
 */

/*
 * =============================================================================
 * INTERVIEW: PROBLEM & INTERFACE
 * =============================================================================
 *
 * Design {@code CBTInserter} for a complete binary tree: {@code insert} attaches
 * the next node in level order; return the parent's value. Maintain a deque of
 * nodes that still need a left or right child (BFS order); the front is always
 * the next parent.
 *
 * Time: O(N) BFS in constructor; O(1) per {@code insert}. Space: O(N) for the
 * candidate queue in the worst case.
 * =============================================================================
 */

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Queue;

// @lc code=start
/**
 * Definition for a binary tree node (provided by LeetCode).
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class CBTInserter {
    private final TreeNode root;
    /** Nodes that do not yet have two children; next parent is at the front. */
    private final Deque<TreeNode> candidates;

    public CBTInserter(TreeNode root) {
        this.root = root;
        this.candidates = new ArrayDeque<>();
        if (root == null) {
            return;
        }
        Queue<TreeNode> bfs = new ArrayDeque<>();
        bfs.offer(root);
        while (!bfs.isEmpty()) {
            TreeNode node = bfs.poll();
            if (node.left == null || node.right == null) {
                candidates.addLast(node);
            }
            if (node.left != null) {
                bfs.offer(node.left);
            }
            if (node.right != null) {
                bfs.offer(node.right);
            }
        }
    }

    public int insert(int val) {
        TreeNode parent = candidates.peekFirst();
        TreeNode child = new TreeNode(val);
        if (parent.left == null) {
            parent.left = child;
        } else {
            parent.right = child;
            candidates.pollFirst();
        }
        candidates.addLast(child);
        return parent.val;
    }

    public TreeNode getRoot() {
        return root;
    }
}
// @lc code=end
