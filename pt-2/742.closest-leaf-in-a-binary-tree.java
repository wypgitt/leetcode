import java.util.*;

/**
 * Algorithm:
 * Convert the tree to an undirected graph by linking each child to its parent,
 * find the target node, then BFS from it. The first leaf reached is the closest
 * leaf by edge distance.
 *
 * Java data structures:
 * IdentityHashMap-backed sets/maps use node object identity as keys, which is
 * appropriate because TreeNode does not define value-based equality.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    private Map<TreeNode, List<TreeNode>> graph;
    private TreeNode target;
    private int targetValue;

    public int findClosestLeaf(TreeNode root, int k) {
        graph = new IdentityHashMap<>();
        target = null;
        targetValue = k;
        build(root, null);

        Queue<TreeNode> q = new ArrayDeque<>();
        Set<TreeNode> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        q.offer(target);
        seen.add(target);
        while (!q.isEmpty()) {
            TreeNode node = q.poll();
            if (node.left == null && node.right == null) {
                return node.val;
            }
            for (TreeNode nei : graph.getOrDefault(node, Collections.emptyList())) {
                if (seen.add(nei)) {
                    q.offer(nei);
                }
            }
        }
        return root.val;
    }

    private void build(TreeNode node, TreeNode parent) {
        if (node == null) {
            return;
        }
        if (node.val == targetValue) {
            target = node;
        }
        graph.computeIfAbsent(node, key -> new ArrayList<>());
        if (parent != null) {
            graph.computeIfAbsent(parent, key -> new ArrayList<>()).add(node);
            graph.get(node).add(parent);
        }
        build(node.left, node);
        build(node.right, node);
    }
}

