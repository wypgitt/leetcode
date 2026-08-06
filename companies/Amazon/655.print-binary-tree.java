import java.util.*;

/**
 * Algorithm:
 * Compute tree height h, allocate h rows and 2^h - 1 columns, then recursively
 * place each node at the midpoint of its allowed column range.
 *
 * Java data structures:
 * List<List<String>> matches LeetCode's required return type. Each row is an
 * ArrayList prefilled with empty strings.
 *
 * Complexity:
 * Time O(h * 2^h) to allocate/fill the matrix, space O(h * 2^h).
 */
class Solution {
    public List<List<String>> printTree(TreeNode root) {
        int h = height(root);
        int rows = h;
        int cols = (1 << h) - 1;
        List<List<String>> ans = new ArrayList<>();
        for (int r = 0; r < rows; r++) {
            List<String> row = new ArrayList<>(Collections.nCopies(cols, ""));
            ans.add(row);
        }
        place(root, 0, 0, cols - 1, ans);
        return ans;
    }

    private int height(TreeNode node) {
        if (node == null) {
            return 0;
        }
        return 1 + Math.max(height(node.left), height(node.right));
    }

    private void place(TreeNode node, int r, int lo, int hi, List<List<String>> ans) {
        if (node == null) {
            return;
        }
        int mid = lo + (hi - lo) / 2;
        ans.get(r).set(mid, String.valueOf(node.val));
        place(node.left, r + 1, lo, mid - 1, ans);
        place(node.right, r + 1, mid + 1, hi, ans);
    }
}

