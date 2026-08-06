/*
 * @lc app=leetcode id=3902 lang=java
 *
 * [3902] Zigzag Level Sum of Binary Tree
 *
 * Breadth-first traversal by level. Odd levels scan left-to-right and stop at
 * the first node without a left child; even levels scan right-to-left and stop
 * at the first node without a right child, matching the Python reference.
 *
 * Time: O(n). Space: O(width).
 */

import java.util.ArrayList;
import java.util.Collections;
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
    public List<Integer> zigzagLevelSum(TreeNode root) {
        List<Integer> answer = new ArrayList<>();
        if (root == null) {
            return answer;
        }

        List<TreeNode> current = new ArrayList<>();
        current.add(root);
        int level = 1;

        while (!current.isEmpty()) {
            List<TreeNode> next = new ArrayList<>();
            for (TreeNode node : current) {
                if (node.left != null) {
                    next.add(node.left);
                }
                if (node.right != null) {
                    next.add(node.right);
                }
            }

            int levelSum = 0;
            if ((level & 1) == 1) {
                for (TreeNode node : current) {
                    if (node.left == null) {
                        break;
                    }
                    levelSum += node.val;
                }
            } else {
                List<TreeNode> reversed = new ArrayList<>(current);
                Collections.reverse(reversed);
                for (TreeNode node : reversed) {
                    if (node.right == null) {
                        break;
                    }
                    levelSum += node.val;
                }
            }

            answer.add(levelSum);
            current = next;
            level++;
        }
        return answer;
    }
}
// @lc code=end
