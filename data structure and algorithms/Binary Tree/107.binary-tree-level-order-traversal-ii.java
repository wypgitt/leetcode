import java.util.*;

/**
 * Algorithm:
 * Collect levels with standard BFS, then reverse the level list so the deepest
 * level appears first.
 *
 * Java data structures:
 * ArrayDeque<TreeNode> is the BFS queue; Collections.reverse reverses the outer
 * ArrayList in place.
 *
 * Complexity:
 * Time O(n), space O(w) queue space plus output.
 */
class Solution {
    public List<List<Integer>> levelOrderBottom(TreeNode root) {
        List<List<Integer>> levels = new ArrayList<>();
        if (root == null) {
            return levels;
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
            levels.add(level);
        }
        Collections.reverse(levels);
        return levels;
    }
}

