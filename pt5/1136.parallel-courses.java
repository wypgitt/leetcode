import java.util.*;

class Solution {
    @SuppressWarnings("unchecked")
    public int minimumSemesters(int n, int[][] relations) {
        List<Integer>[] graph = new ArrayList[n + 1];
        for (int i = 1; i <= n; i++) {
            graph[i] = new ArrayList<>();
        }
        int[] indegree = new int[n + 1];

        for (int[] relation : relations) {
            int before = relation[0];
            int after = relation[1];
            graph[before].add(after);
            indegree[after]++;
        }

        Queue<Integer> queue = new ArrayDeque<>();
        for (int course = 1; course <= n; course++) {
            if (indegree[course] == 0) {
                queue.offer(course);
            }
        }

        int taken = 0;
        int semesters = 0;
        while (!queue.isEmpty()) {
            semesters++;
            int levelSize = queue.size();
            for (int i = 0; i < levelSize; i++) {
                int course = queue.poll();
                taken++;
                for (int nextCourse : graph[course]) {
                    indegree[nextCourse]--;
                    if (indegree[nextCourse] == 0) {
                        queue.offer(nextCourse);
                    }
                }
            }
        }

        return taken == n ? semesters : -1;
    }
}
