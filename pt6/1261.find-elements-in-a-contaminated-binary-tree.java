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

class FindElements {
    private final Set<Integer> values = new HashSet<>();

    public FindElements(TreeNode root) {
        recover(root, 0);
    }

    public boolean find(int target) {
        return values.contains(target);
    }

    private void recover(TreeNode node, int value) {
        if (node == null) {
            return;
        }
        node.val = value;
        values.add(value);
        recover(node.left, 2 * value + 1);
        recover(node.right, 2 * value + 2);
    }
}

/*
Explanation

Recovery is deterministic: root is 0, left child is 2*x + 1, and right child is
2*x + 2. DFS once in the constructor, assign values, and store them in a
HashSet.

The HashSet makes find(target) average O(1). This front-loads the tree recovery
work instead of walking the tree for every query.

Edge cases: missing children are skipped; a single root recovers to 0; targets
outside the recovered set return false.

Time complexity: constructor O(n), find O(1) average.
Space complexity: O(n).
*/
