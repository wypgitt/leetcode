import java.util.HashSet;
import java.util.Set;

/*
class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;
    TreeNode(int x) { val = x; }
}
*/

class Solution {
    public boolean twoSumBSTs(TreeNode root1, TreeNode root2, int target) {
        Set<Integer> values = new HashSet<>();
        collect(root1, values);
        return search(root2, target, values);
    }

    private void collect(TreeNode node, Set<Integer> values) {
        if (node == null) {
            return;
        }
        values.add(node.val);
        collect(node.left, values);
        collect(node.right, values);
    }

    private boolean search(TreeNode node, int target, Set<Integer> values) {
        if (node == null) {
            return false;
        }
        if (values.contains(target - node.val)) {
            return true;
        }
        return search(node.left, target, values) || search(node.right, target, values);
    }
}

/*
Explanation

Traverse the first BST and store every value in a HashSet. Then traverse the
second BST and check whether target - node.val exists in that set.

Although the inputs are BSTs, ordering is not required because the question is
existence. A HashSet gives average O(1) complement lookup and keeps the
solution simpler than coordinating two tree iterators.

Edge cases: either tree can be null; duplicate values are harmless because the
two chosen nodes come from different trees; negative values work with the same
complement formula.

Time complexity: O(n + m).
Space complexity: O(n) for the first tree's values plus recursion stack.
*/
