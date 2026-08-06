import java.util.*;

/**
 * Algorithm:
 * Topological sort with indegrees. Append each zero-indegree course to the
 * order and remove its outgoing edges. If a cycle remains, not all courses are
 * output and the answer is empty.
 *
 * Java data structures:
 * ArrayList<Integer>[] stores adjacency; ArrayDeque<Integer> stores the current
 * zero-indegree frontier.
 *
 * Complexity:
 * Time O(V + E), space O(V + E).
 */
class Solution {
    public int[] findOrder(int numCourses, int[][] prerequisites) {
        List<Integer>[] graph = new ArrayList[numCourses];
        for (int i = 0; i < numCourses; i++) {
            graph[i] = new ArrayList<>();
        }
        int[] indegree = new int[numCourses];
        for (int[] edge : prerequisites) {
            int course = edge[0];
            int pre = edge[1];
            graph[pre].add(course);
            indegree[course]++;
        }
        Queue<Integer> q = new ArrayDeque<>();
        for (int i = 0; i < numCourses; i++) {
            if (indegree[i] == 0) {
                q.offer(i);
            }
        }
        int[] order = new int[numCourses];
        int size = 0;
        while (!q.isEmpty()) {
            int node = q.poll();
            order[size++] = node;
            for (int next : graph[node]) {
                if (--indegree[next] == 0) {
                    q.offer(next);
                }
            }
        }
        return size == numCourses ? order : new int[0];
    }
}

