import java.util.*;

/**
 * Algorithm:
 * Backtrack over root-to-leaf paths. The path list stores the current route,
 * and the remaining sum tracks how much is still needed. At a leaf, copy the
 * path when the remaining sum is zero.
 *
 * Java data structures:
 * ArrayList<Integer> is used for the mutable path; valid answers are copied
 * with new ArrayList<>(path).
 *
 * Complexity:
 * Time O(n * h) in the worst case due to path copies, space O(h) recursion
 * excluding output.
 */
class Solution {
    private List<List<Integer>> ans;
    private List<Integer> path;

    public List<List<Integer>> pathSum(TreeNode root, int targetSum) {
        ans = new ArrayList<>();
        path = new ArrayList<>();
        dfs(root, targetSum);
        return ans;
    }

    private void dfs(TreeNode node, int remain) {
        if (node == null) {
            return;
        }
        path.add(node.val);
        remain -= node.val;
        if (node.left == null && node.right == null && remain == 0) {
            ans.add(new ArrayList<>(path));
        } else {
            dfs(node.left, remain);
            dfs(node.right, remain);
        }
        path.remove(path.size() - 1);
    }
}

