/*
 * LeetCode 1339 - Maximum Product of Splitted Binary Tree
 *
 * TreeNode is provided by LeetCode.
 */
class Solution {
    private static final int MOD = 1_000_000_007;
    private long totalSum;
    private long best;

    public int maxProduct(TreeNode root) {
        totalSum = subtreeSum(root);
        best = 0;
        findBest(root);
        return (int) (best % MOD);
    }

    private long subtreeSum(TreeNode node) {
        if (node == null) {
            return 0;
        }
        return node.val + subtreeSum(node.left) + subtreeSum(node.right);
    }

    private long findBest(TreeNode node) {
        if (node == null) {
            return 0;
        }

        long current = node.val + findBest(node.left) + findBest(node.right);
        best = Math.max(best, current * (totalSum - current));
        return current;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Removing one edge creates one subtree with sum s and the remaining tree with
 * sum totalSum - s. The product is `s * (totalSum - s)`. We compute every
 * possible subtree sum and keep the largest product.
 *
 * Java data structures:
 * Recursive DFS returns subtree sums as `long`. `long` is important because
 * the product can exceed the range of int before applying modulo.
 *
 * Why modulo at the end:
 * Modulo changes ordering, so we compare raw products first and only take
 * modulo for the final returned value.
 *
 * Complexity:
 * Time O(n), two DFS passes.
 * Space O(h), recursion stack height.
 */
