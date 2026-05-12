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
    private Set<Integer> deleted;
    private List<TreeNode> forest;

    public List<TreeNode> delNodes(TreeNode root, int[] to_delete) {
        deleted = new HashSet<>();
        for (int value : to_delete) {
            deleted.add(value);
        }

        forest = new ArrayList<>();
        prune(root, true);
        return forest;
    }

    private TreeNode prune(TreeNode node, boolean isRoot) {
        if (node == null) {
            return null;
        }

        boolean isDeleted = deleted.contains(node.val);
        if (isRoot && !isDeleted) {
            forest.add(node);
        }

        node.left = prune(node.left, isDeleted);
        node.right = prune(node.right, isDeleted);
        return isDeleted ? null : node;
    }
}

