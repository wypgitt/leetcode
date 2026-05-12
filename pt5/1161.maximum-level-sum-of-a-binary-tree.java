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
    public int maxLevelSum(TreeNode root) {
        Queue<TreeNode> queue = new ArrayDeque<>();
        queue.offer(root);
        int bestSum = Integer.MIN_VALUE;
        int bestLevel = 1;
        int level = 1;

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            int levelSum = 0;
            for (int i = 0; i < levelSize; i++) {
                TreeNode node = queue.poll();
                levelSum += node.val;
                if (node.left != null) {
                    queue.offer(node.left);
                }
                if (node.right != null) {
                    queue.offer(node.right);
                }
            }

            if (levelSum > bestSum) {
                bestSum = levelSum;
                bestLevel = level;
            }
            level++;
        }

        return bestLevel;
    }
}

