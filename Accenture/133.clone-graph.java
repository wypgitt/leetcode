import java.util.*;

/**
 * Algorithm:
 * DFS clone with memoization. When a node is first seen, create its clone and
 * store it before cloning neighbors, which handles cycles.
 *
 * Java data structures:
 * IdentityHashMap<Node, Node> keys by object identity, matching graph-node
 * identity semantics rather than value equality.
 *
 * Complexity:
 * Time O(V + E), space O(V).
 */
class Solution {
    private Map<Node, Node> clones;

    public Node cloneGraph(Node node) {
        clones = new IdentityHashMap<>();
        return clone(node);
    }

    private Node clone(Node cur) {
        if (cur == null) {
            return null;
        }
        if (clones.containsKey(cur)) {
            return clones.get(cur);
        }
        Node copied = new Node(cur.val);
        clones.put(cur, copied);
        copied.neighbors = new ArrayList<>();
        for (Node nei : cur.neighbors) {
            copied.neighbors.add(clone(nei));
        }
        return copied;
    }
}

