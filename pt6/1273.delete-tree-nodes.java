import java.util.ArrayList;
import java.util.List;

class Solution {
    public int deleteTreeNodes(int nodes, int[] parent, int[] value) {
        List<Integer>[] children = new ArrayList[nodes];
        for (int i = 0; i < nodes; i++) {
            children[i] = new ArrayList<>();
        }

        int root = 0;
        for (int node = 0; node < nodes; node++) {
            if (parent[node] == -1) {
                root = node;
            } else {
                children[parent[node]].add(node);
            }
        }

        return dfs(root, children, value)[1];
    }

    private int[] dfs(int node, List<Integer>[] children, int[] value) {
        int sum = value[node];
        int count = 1;

        for (int child : children[node]) {
            int[] result = dfs(child, children, value);
            sum += result[0];
            count += result[1];
        }

        if (sum == 0) {
            return new int[] {0, 0};
        }
        return new int[] {sum, count};
    }
}

/*
Explanation

Build child lists from the parent array, then run postorder DFS. Each subtree
returns two values: subtree sum and remaining node count. If the subtree sum is
0, the whole subtree is deleted and contributes count 0 upward.

Postorder traversal is required because a node's deletion depends on all
descendants. An array of ArrayLists is efficient because node ids are 0..n-1.

Edge cases: the root can be deleted; nested zero-sum subtrees; negative values
are handled by normal addition.

Time complexity: O(n).
Space complexity: O(n).
*/
