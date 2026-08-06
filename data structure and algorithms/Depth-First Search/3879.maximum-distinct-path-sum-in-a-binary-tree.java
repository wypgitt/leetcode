/*
 * @lc app=leetcode id=3879 lang=java
 *
 * [3879] Maximum Distinct Path Sum in a Binary Tree
 *
 * Convert the binary tree to an undirected adjacency list. Start DFS from every
 * node, carrying a set of values already used; paths stop before repeating a
 * value. Track the maximum sum reached.
 *
 * Java note: HashMap<TreeNode,Integer> maps node references to graph indices.
 * HashSet<Integer> tracks values on the current path with backtracking.
 */

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

// @lc code=start
/**
 * Definition for a binary tree node.
 * public class TreeNode {
 *     int val;
 *     TreeNode left;
 *     TreeNode right;
 *     TreeNode() {}
 *     TreeNode(int val) { this.val = val; }
 *     TreeNode(int val, TreeNode left, TreeNode right) {
 *         this.val = val;
 *         this.left = left;
 *         this.right = right;
 *     }
 * }
 */
class Solution {
    private int[] values;
    private List<Integer>[] graph;
    private long answer;

    public long maxSum(TreeNode root) {
        Map<TreeNode, Integer> indexByNode = new HashMap<>();
        List<Integer> valueList = new ArrayList<>();
        List<List<Integer>> graphList = new ArrayList<>();

        ArrayDeque<TreeNode> stack = new ArrayDeque<>();
        if (root != null) {
            stack.push(root);
        }
        while (!stack.isEmpty()) {
            TreeNode node = stack.pop();
            int index = addNode(node, indexByNode, valueList, graphList);

            if (node.left != null) {
                int left = addNode(node.left, indexByNode, valueList, graphList);
                graphList.get(index).add(left);
                graphList.get(left).add(index);
                stack.push(node.left);
            }
            if (node.right != null) {
                int right = addNode(node.right, indexByNode, valueList, graphList);
                graphList.get(index).add(right);
                graphList.get(right).add(index);
                stack.push(node.right);
            }
        }

        int n = valueList.size();
        values = new int[n];
        graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            values[i] = valueList.get(i);
            graph[i] = new ArrayList<>(graphList.get(i));
        }

        answer = Long.MIN_VALUE;
        for (int start = 0; start < n; start++) {
            Set<Integer> used = new HashSet<>();
            used.add(values[start]);
            dfs(start, -1, values[start], used);
        }
        return answer;
    }

    private int addNode(TreeNode node, Map<TreeNode, Integer> indexByNode, List<Integer> values,
                        List<List<Integer>> graph) {
        Integer existing = indexByNode.get(node);
        if (existing != null) {
            return existing;
        }
        int index = values.size();
        indexByNode.put(node, index);
        values.add(node.val);
        graph.add(new ArrayList<>());
        return index;
    }

    private void dfs(int node, int parent, long currentSum, Set<Integer> used) {
        answer = Math.max(answer, currentSum);
        for (int nei : graph[node]) {
            if (nei == parent || used.contains(values[nei])) {
                continue;
            }
            used.add(values[nei]);
            dfs(nei, node, currentSum + values[nei], used);
            used.remove(values[nei]);
        }
    }
}
// @lc code=end
