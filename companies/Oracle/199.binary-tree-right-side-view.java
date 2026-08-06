import java.util.*;

/**
 * Algorithm:
 * BFS by levels and record the last node seen in each level, which is the node
 * visible from the right side.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is the BFS queue.
 *
 * Complexity:
 * Time O(n), space O(w).
 */
class Solution {
    public List<Integer> rightSideView(TreeNode root) {
        List<Integer> ans = new ArrayList<>();
        if (root == null) {
            return ans;
        }
        Queue<TreeNode> q = new ArrayDeque<>();
        q.offer(root);
        while (!q.isEmpty()) {
            int size = q.size();
            for (int i = 0; i < size; i++) {
                TreeNode node = q.poll();
                if (i == size - 1) {
                    ans.add(node.val);
                }
                if (node.left != null) {
                    q.offer(node.left);
                }
                if (node.right != null) {
                    q.offer(node.right);
                }
            }
        }
        return ans;
    }
}

