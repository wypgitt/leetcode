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
    public TreeNode lcaDeepestLeaves(TreeNode root) {
        return dfs(root).node;
    }

    private Result dfs(TreeNode node) {
        if (node == null) {
            return new Result(0, null);
        }

        Result left = dfs(node.left);
        Result right = dfs(node.right);
        if (left.depth == right.depth) {
            return new Result(left.depth + 1, node);
        }
        if (left.depth > right.depth) {
            return new Result(left.depth + 1, left.node);
        }
        return new Result(right.depth + 1, right.node);
    }

    private static class Result {
        int depth;
        TreeNode node;

        Result(int depth, TreeNode node) {
            this.depth = depth;
            this.node = node;
        }
    }
}

