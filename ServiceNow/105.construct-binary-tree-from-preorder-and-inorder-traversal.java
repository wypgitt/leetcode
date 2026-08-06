import java.util.*;

/**
 * Algorithm:
 * Preorder gives the root first; inorder splits values into left and right
 * subtrees. A value-to-index map makes every split O(1), so each node is built
 * exactly once.
 *
 * Java data structures:
 * HashMap<Integer, Integer> maps inorder values to indices.
 *
 * Complexity:
 * Time O(n), space O(n) for the map plus O(h) recursion stack.
 */
class Solution {
    private int[] preorder;
    private Map<Integer, Integer> index;

    public TreeNode buildTree(int[] preorder, int[] inorder) {
        this.preorder = preorder;
        index = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) {
            index.put(inorder[i], i);
        }
        return build(0, preorder.length - 1, 0, inorder.length - 1);
    }

    private TreeNode build(int preL, int preR, int inL, int inR) {
        if (preL > preR) {
            return null;
        }
        int rootVal = preorder[preL];
        int mid = index.get(rootVal);
        int leftSize = mid - inL;
        TreeNode root = new TreeNode(rootVal);
        root.left = build(preL + 1, preL + leftSize, inL, mid - 1);
        root.right = build(preL + leftSize + 1, preR, mid + 1, inR);
        return root;
    }
}

