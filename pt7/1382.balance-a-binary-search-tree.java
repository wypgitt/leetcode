import java.util.ArrayList;
import java.util.List;

/*
 * LeetCode 1382 - Balance a Binary Search Tree
 *
 * TreeNode is provided by LeetCode.
 */
class Solution {
    public TreeNode balanceBST(TreeNode root) {
        List<Integer> values = new ArrayList<>();
        inorder(root, values);
        return build(values, 0, values.size() - 1);
    }

    private void inorder(TreeNode node, List<Integer> values) {
        if (node == null) {
            return;
        }
        inorder(node.left, values);
        values.add(node.val);
        inorder(node.right, values);
    }

    private TreeNode build(List<Integer> values, int left, int right) {
        if (left > right) {
            return null;
        }

        int mid = left + (right - left) / 2;
        TreeNode node = new TreeNode(values.get(mid));
        node.left = build(values, left, mid - 1);
        node.right = build(values, mid + 1, right);
        return node;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Inorder traversal of a BST gives sorted values. A height-balanced BST is
 * built from a sorted array by recursively choosing the middle element as root.
 *
 * Java data structures:
 * `ArrayList<Integer>` stores the sorted inorder values. Recursive construction
 * uses index ranges instead of copying sublists.
 *
 * Edge cases:
 * - Empty tree returns null.
 * - Already balanced input may produce a different but still valid balanced BST.
 * - Duplicate values remain in sorted inorder order.
 *
 * Complexity:
 * Time O(n), one traversal and one rebuild.
 * Space O(n), for values and recursion stack.
 */
