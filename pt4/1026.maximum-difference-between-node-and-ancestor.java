/*
 * 1026. Maximum Difference Between Node and Ancestor
 */

// LeetCode provides this class:
// class TreeNode {
//     int val;
//     TreeNode left;
//     TreeNode right;
//     TreeNode() {}
//     TreeNode(int val) { this.val = val; }
//     TreeNode(int val, TreeNode left, TreeNode right) {
//         this.val = val;
//         this.left = left;
//         this.right = right;
//     }
// }

class Solution {
    public int maxAncestorDiff(TreeNode root) {
        return dfs(root, root.val, root.val);
    }

    private int dfs(TreeNode node, int pathMin, int pathMax) {
        if (node == null) {
            return pathMax - pathMin;
        }

        pathMin = Math.min(pathMin, node.val);
        pathMax = Math.max(pathMax, node.val);

        return Math.max(
            dfs(node.left, pathMin, pathMax),
            dfs(node.right, pathMin, pathMax)
        );
    }
}

/*
Interview Explanation

Core idea:
For any node, the best ancestor difference only depends on the minimum and
maximum value along the path from the root to that node. We do not need to keep
the entire ancestor list.

Java data structures:
- Recursion naturally carries the root-to-current-node path.
- Two primitive ints, pathMin and pathMax, summarize every ancestor needed for
  the answer.

Algorithm:
1. DFS from the root.
2. At each node, update the path minimum and maximum.
3. When a null child is reached, return pathMax - pathMin for that completed
   path.
4. Take the maximum over left and right subtrees.

Correctness:
Every ancestor-descendant pair lies on some root-to-node path. The maximum
absolute difference among values on that path is max - min. DFS computes that
quantity for every path and returns the largest one, so it finds the best valid
ancestor-node difference.

Complexity:
Each tree node is visited once, so time is O(n). The recursion stack is O(h),
where h is the tree height.

Edge cases:
- Skewed tree: pathMin/pathMax update along the chain.
- Root value can be the max or min.
- Smallest allowed tree with two nodes works naturally.
*/
