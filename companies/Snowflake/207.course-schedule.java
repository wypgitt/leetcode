import java.util.*;

/**
 * Algorithm:
 * Topological sort with indegrees. Courses with indegree zero can be taken;
 * removing them reduces indegrees of dependent courses. All courses are
 * finishable iff every course is removed.
 *
 * Java data structures:
 * ArrayList<Integer>[] is the adjacency list; ArrayDeque<Integer> is the queue.
 *
 * Complexity:
 * Time O(V + E), space O(V + E).
 */
class Solution {
    public boolean canFinish(int numCourses, int[][] prerequisites) {
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
        int taken = 0;
        while (!q.isEmpty()) {
            int node = q.poll();
            taken++;
            for (int next : graph[node]) {
                if (--indegree[next] == 0) {
                    q.offer(next);
                }
            }
        }
        return taken == numCourses;
    }
}

