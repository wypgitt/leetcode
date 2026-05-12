import java.util.ArrayDeque;
import java.util.Queue;

/*
 * LeetCode 1302 - Deepest Leaves Sum
 *
 * Definition for a binary tree node is provided by LeetCode:
 * class TreeNode {
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
    public int deepestLeavesSum(TreeNode root) {
        if (root == null) {
            return 0;
        }

        Queue<TreeNode> queue = new ArrayDeque<>();
        queue.offer(root);
        int levelSum = 0;

        while (!queue.isEmpty()) {
            levelSum = 0;
            int levelSize = queue.size();

            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                levelSum += node.val;

                if (node.left != null) {
                    queue.offer(node.left);
                }
                if (node.right != null) {
                    queue.offer(node.right);
                }
            }
        }

        return levelSum;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * We need only the last level of the tree. A breadth-first search naturally
 * visits nodes level by level, so we overwrite `levelSum` for every level. When
 * the queue becomes empty, the most recent sum is the deepest leaves sum.
 *
 * Java data structures:
 * `Queue<TreeNode>` backed by `ArrayDeque` gives O(1) enqueue and dequeue.
 * `LinkedList` would also work, but `ArrayDeque` is the usual Java choice for
 * queue/stack behavior when we do not need random access.
 *
 * Edge cases:
 * - Empty root returns 0 defensively.
 * - Single-node tree returns the root value.
 * - Skewed tree works because each BFS layer simply has one node.
 *
 * Complexity:
 * Time O(n), every node is visited once.
 * Space O(w), where w is the maximum tree width stored in the queue.
 */
