import java.util.ArrayList;
import java.util.List;

/*
 * LeetCode 1305 - All Elements in Two Binary Search Trees
 *
 * TreeNode is provided by LeetCode.
 */
class Solution {
    public List<Integer> getAllElements(TreeNode root1, TreeNode root2) {
        List<Integer> first = new ArrayList<>();
        List<Integer> second = new ArrayList<>();
        inorder(root1, first);
        inorder(root2, second);

        List<Integer> merged = new ArrayList<>(first.size() + second.size());
        int i = 0;
        int j = 0;

        while (i < first.size() && j < second.size()) {
            if (first.get(i) <= second.get(j)) {
                merged.add(first.get(i++));
            } else {
                merged.add(second.get(j++));
            }
        }

        while (i < first.size()) {
            merged.add(first.get(i++));
        }
        while (j < second.size()) {
            merged.add(second.get(j++));
        }

        return merged;
    }

    private void inorder(TreeNode node, List<Integer> values) {
        if (node == null) {
            return;
        }
        inorder(node.left, values);
        values.add(node.val);
        inorder(node.right, values);
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Inorder traversal of a BST returns values in sorted order. After traversing
 * both trees, the problem becomes merging two sorted arrays, exactly like the
 * merge step in merge sort.
 *
 * Java data structures:
 * `ArrayList<Integer>` stores each traversal and the merged result. ArrayList
 * has efficient append and indexed reads, which are exactly what the two-pointer
 * merge needs.
 *
 * Why choose this approach:
 * Collecting all values and sorting would cost O((m+n) log(m+n)). Using the BST
 * property gives sorted lists for free during traversal and reduces the merge
 * to linear time.
 *
 * Edge cases:
 * - Either root can be null; its inorder list is empty.
 * - Duplicate values are preserved by adding from the first list on `<=`.
 * - Both roots null returns an empty list.
 *
 * Complexity:
 * Time O(m+n), where m and n are the node counts.
 * Space O(m+n) for the lists, plus O(h1+h2) recursion stack.
 */
