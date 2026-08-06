import java.util.*;

/**
 * Algorithm:
 * For each possible root value, recursively generate every left subtree from
 * smaller values and every right subtree from larger values, then combine each
 * left/right pair under a new root.
 *
 * Java data structures:
 * HashMap<String, List<TreeNode>> memoizes ranges, mirroring Python lru_cache.
 * Null is used as the single empty-subtree option.
 *
 * Complexity:
 * O(C_n * n) time and space for C_n generated BSTs; recursion depth O(n).
 */
class Solution {
    private Map<String, List<TreeNode>> memo;

    public List<TreeNode> generateTrees(int n) {
        memo = new HashMap<>();
        return build(1, n);
    }

    private List<TreeNode> build(int lo, int hi) {
        String key = lo + "," + hi;
        if (memo.containsKey(key)) {
            return memo.get(key);
        }
        List<TreeNode> trees = new ArrayList<>();
        if (lo > hi) {
            trees.add(null);
            memo.put(key, trees);
            return trees;
        }
        for (int rootVal = lo; rootVal <= hi; rootVal++) {
            for (TreeNode left : build(lo, rootVal - 1)) {
                for (TreeNode right : build(rootVal + 1, hi)) {
                    TreeNode root = new TreeNode(rootVal);
                    root.left = left;
                    root.right = right;
                    trees.add(root);
                }
            }
        }
        memo.put(key, trees);
        return trees;
    }
}

