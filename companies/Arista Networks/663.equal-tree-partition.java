import java.util.*;

/**
 * Algorithm:
 * Compute every subtree sum with DFS. The whole tree sum cannot be used as a
 * cut, so remove it. A valid partition exists exactly when the total is even
 * and some remaining subtree has sum total / 2.
 *
 * Java data structures:
 * ArrayList<Integer> stores all subtree sums. It preserves duplicates, which
 * matters when total is zero.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public boolean checkEqualTree(TreeNode root) {
        List<Integer> sums = new ArrayList<>();
        int total = dfs(root, sums);
        sums.remove(sums.size() - 1);
        return total % 2 == 0 && sums.contains(total / 2);
    }

    private int dfs(TreeNode node, List<Integer> sums) {
        if (node == null) {
            return 0;
        }
        int total = node.val + dfs(node.left, sums) + dfs(node.right, sums);
        sums.add(total);
        return total;
    }
}

