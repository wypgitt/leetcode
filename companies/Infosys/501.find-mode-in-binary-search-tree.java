/*
 * @lc app=leetcode id=501 lang=java
 *
 * [501] Find Mode in Binary Search Tree
 *
 * In-order traversal of a BST visits equal values contiguously. Morris
 * traversal gives that order without recursion or an explicit stack; count the
 * current run and update the mode list.
 *
 * Java note: Morris traversal temporarily threads predecessor.right to current
 * and restores it before moving on.
 *
 * Time: O(n). Space: O(1) excluding the returned modes.
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
/**
 * Definition for a binary tree node.
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
class Solution {
    private final List<Integer> modes = new ArrayList<>();
    private int previousValue;
    private boolean hasPrevious;
    private int currentCount;
    private int maxCount;

    public int[] findMode(TreeNode root) {
        TreeNode current = root;
        while (current != null) {
            if (current.left == null) {
                visit(current.val);
                current = current.right;
                continue;
            }

            TreeNode predecessor = current.left;
            while (predecessor.right != null && predecessor.right != current) {
                predecessor = predecessor.right;
            }

            if (predecessor.right == null) {
                predecessor.right = current;
                current = current.left;
            } else {
                predecessor.right = null;
                visit(current.val);
                current = current.right;
            }
        }

        int[] answer = new int[modes.size()];
        for (int i = 0; i < modes.size(); i++) {
            answer[i] = modes.get(i);
        }
        return answer;
    }

    private void visit(int value) {
        if (hasPrevious && value == previousValue) {
            currentCount++;
        } else {
            previousValue = value;
            hasPrevious = true;
            currentCount = 1;
        }

        if (currentCount > maxCount) {
            maxCount = currentCount;
            modes.clear();
            modes.add(value);
        } else if (currentCount == maxCount) {
            modes.add(value);
        }
    }
}
// @lc code=end
