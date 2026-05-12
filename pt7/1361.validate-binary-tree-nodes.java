import java.util.ArrayDeque;
import java.util.Deque;

/*
 * LeetCode 1361 - Validate Binary Tree Nodes
 */
class Solution {
    public boolean validateBinaryTreeNodes(int n, int[] leftChild, int[] rightChild) {
        int[] indegree = new int[n];

        for (int parent = 0; parent < n; parent++) {
            if (leftChild[parent] != -1 && ++indegree[leftChild[parent]] > 1) {
                return false;
            }
            if (rightChild[parent] != -1 && ++indegree[rightChild[parent]] > 1) {
                return false;
            }
        }

        int root = -1;
        for (int node = 0; node < n; node++) {
            if (indegree[node] == 0) {
                if (root != -1) {
                    return false;
                }
                root = node;
            }
        }
        if (root == -1) {
            return false;
        }

        boolean[] seen = new boolean[n];
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(root);
        int visited = 0;

        while (!stack.isEmpty()) {
            int node = stack.pop();
            if (seen[node]) {
                return false;
            }

            seen[node] = true;
            visited++;

            if (leftChild[node] != -1) {
                stack.push(leftChild[node]);
            }
            if (rightChild[node] != -1) {
                stack.push(rightChild[node]);
            }
        }

        return visited == n;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * A valid binary tree must have exactly one root, every non-root node must have
 * exactly one parent, and all nodes must be reachable from the root without
 * cycles.
 *
 * Java data structures:
 * `int[] indegree` counts parents. `boolean[] seen` plus an `ArrayDeque` DFS
 * verifies reachability and detects revisits.
 *
 * Edge cases:
 * - A node with two parents fails immediately.
 * - Disconnected components produce either multiple roots or too few visited
 *   nodes.
 * - Cycles produce no root or a DFS revisit.
 *
 * Complexity:
 * Time O(n).
 * Space O(n).
 */
