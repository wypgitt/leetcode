import java.util.*;

/**
 * Algorithm:
 * Use normal BFS for level grouping, then reverse every other level's values.
 * Keeping child enqueue order standard preserves a simple BFS invariant.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is the BFS queue; Collections.reverse flips alternate
 * level lists in place.
 *
 * Complexity:
 * Time O(n), space O(w) for the queue, excluding output.
 */
class Solution {
    public List<List<Integer>> zigzagLevelOrder(TreeNode root) {
        List<List<Integer>> ans = new ArrayList<>();
        if (root == null) {
            return ans;
        }
        Queue<TreeNode> q = new ArrayDeque<>();
        q.offer(root);
        boolean leftToRight = true;
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
            if (!leftToRight) {
                Collections.reverse(level);
            }
            ans.add(level);
            leftToRight = !leftToRight;
        }
        return ans;
    }
}

