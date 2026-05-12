import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/*
 * 1059. All Paths from Source Lead to Destination
 */
class Solution {
    public boolean leadsToDestination(int n, int[][] edges, int source, int destination) {
        @SuppressWarnings("unchecked")
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
        }

        int[] state = new int[n];
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[] {source, 0});

        while (!stack.isEmpty()) {
            int[] frame = stack.peek();
            int node = frame[0];

            if (state[node] == 0) {
                if (graph[node].isEmpty()) {
                    if (node != destination) {
                        return false;
                    }
                    state[node] = 2;
                    stack.pop();
                    continue;
                }
                state[node] = 1;
            }

            if (frame[1] == graph[node].size()) {
                state[node] = 2;
                stack.pop();
                continue;
            }

            int neighbor = graph[node].get(frame[1]);
            frame[1]++;

            if (state[neighbor] == 1) {
                return false;
            }
            if (state[neighbor] == 0) {
                stack.push(new int[] {neighbor, 0});
            }
        }

        return true;
    }
}

/*
Interview Explanation

Core idea:
All paths from source must end at destination, and the number of paths must be
finite. A reachable dead end that is not destination fails. A reachable cycle
also fails because it creates an infinite path or infinitely many paths.

Java data structures:
- ArrayList<Integer>[] adjacency list represents the directed graph.
- int[] state implements DFS coloring:
  0 = unvisited, 1 = currently visiting, 2 = proven safe.
- ArrayDeque<int[]> is an explicit DFS stack. Each frame stores the node and
  the next outgoing edge index to process. This avoids Java recursion-depth
  risk on a 10,000-node path.

Algorithm:
1. Build the directed graph.
2. DFS from source with an explicit stack.
3. If a node has no outgoing edges, it is valid only if it is destination.
4. If traversal reaches a state-1 node, a reachable cycle exists, so return false.
5. A node becomes safe only when every outgoing neighbor is safe.

Correctness:
The terminal-node check enforces that any path that stops must stop at
destination. The visiting state detects cycles reachable from source, which
violates the finite-path requirement. If every outgoing neighbor of a node is
safe, then every path from that node also ends at destination. Thus DFS returns
true exactly when all paths from source lead to destination.

Complexity:
Each reachable node is processed once and each reachable edge is checked once,
so time is O(n + e). The graph and state arrays use O(n + e) space, and the
explicit stack can be O(n).

Edge cases:
- Source equals destination with no outgoing edges returns true.
- A path to a non-destination dead end returns false.
- A reachable self-loop returns false.
- Unreachable bad components do not matter.
*/
