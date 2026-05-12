import java.util.*;

class TreeNode {
    int val;
    TreeNode left;
    TreeNode right;

    TreeNode() {}

    TreeNode(int val) {
        this.val = val;
    }

    TreeNode(int val, TreeNode left, TreeNode right) {
        this.val = val;
        this.left = left;
        this.right = right;
    }
}

class Solution {
    private int leftSize;
    private int rightSize;
    private int target;

    public boolean btreeGameWinningMove(TreeNode root, int n, int x) {
        target = x;
        size(root);
        int parentSide = n - leftSize - rightSize - 1;
        return Math.max(parentSide, Math.max(leftSize, rightSize)) > n / 2;
    }

    private int size(TreeNode node) {
        if (node == null) {
            return 0;
        }

        int left = size(node.left);
        int right = size(node.right);
        if (node.val == target) {
            leftSize = left;
            rightSize = right;
        }
        return left + right + 1;
    }
}

