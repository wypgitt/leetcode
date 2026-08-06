import java.util.*;

/**
 * Algorithm:
 * Build a parent -> children adjacency list, then BFS from the killed process.
 * Every descendant is killed and added to the answer.
 *
 * Java data structures:
 * HashMap<Integer, List<Integer>> is the adjacency list. ArrayDeque is the BFS
 * queue.
 *
 * Complexity:
 * Time O(n), space O(n).
 */
class Solution {
    public List<Integer> killProcess(List<Integer> pid, List<Integer> ppid, int kill) {
        Map<Integer, List<Integer>> children = new HashMap<>();
        for (int i = 0; i < pid.size(); i++) {
            children.computeIfAbsent(ppid.get(i), key -> new ArrayList<>()).add(pid.get(i));
        }

        List<Integer> ans = new ArrayList<>();
        Queue<Integer> q = new ArrayDeque<>();
        q.offer(kill);
        while (!q.isEmpty()) {
            int cur = q.poll();
            ans.add(cur);
            for (int child : children.getOrDefault(cur, Collections.emptyList())) {
                q.offer(child);
            }
        }
        return ans;
    }
}

