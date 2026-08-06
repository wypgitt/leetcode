import java.util.*;

/**
 * Algorithm:
 * Postorder gives the root last; inorder splits the subtree around that root.
 * Recursively build left and right ranges using a value-to-index map.
 *
 * Java data structures:
 * HashMap<Integer, Integer> avoids scanning inorder for every root.
 *
 * Complexity:
 * Time O(n), space O(n) for the map plus O(h) recursion stack.
 */
class Solution {
    private int[] postorder;
    private Map<Integer, Integer> index;

    public TreeNode buildTree(int[] inorder, int[] postorder) {
        this.postorder = postorder;
        index = new HashMap<>();
        for (int i = 0; i < inorder.length; i++) {
            index.put(inorder[i], i);
        }
        return build(0, inorder.length - 1, 0, postorder.length - 1);
    }

    private TreeNode build(int inL, int inR, int postL, int postR) {
        if (inL > inR) {
            return null;
        }
        int rootVal = postorder[postR];
        int mid = index.get(rootVal);
        int leftSize = mid - inL;
        TreeNode root = new TreeNode(rootVal);
        root.left = build(inL, mid - 1, postL, postL + leftSize - 1);
        root.right = build(mid + 1, inR, postL + leftSize, postR - 1);
        return root;
    }
}

