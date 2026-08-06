import java.util.*;

/**
 * Algorithm:
 * Breadth-first search processes the tree level by level. For each loop, the
 * current queue size is exactly the number of nodes in that depth, so those
 * values form one output row.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is used as a FIFO queue. It is faster and cleaner than
 * the legacy LinkedList queue for this use case.
 *
 * Complexity:
 * Time O(n), space O(w), where w is the maximum tree width.
 */
class Solution {
    public List<List<Integer>> levelOrder(TreeNode root) {
        List<List<Integer>> ans = new ArrayList<>();
        if (root == null) {
            return ans;
        }
        Queue<TreeNode> q = new ArrayDeque<>();
        q.offer(root);
        while (!q.isEmpty()) {
            int size = q.size();
            List<Integer> level = new ArrayList<>(size);
            for (int i = 0; i < size; i++) {
                TreeNode node = q.poll();
                level.add(node.val);
                if (node.left != null) {
                    q.offer(node.left);
                }
                if (node.right != null) {
                    q.offer(node.right);
                }
            }
            ans.add(level);
        }
        return ans;
    }
}

