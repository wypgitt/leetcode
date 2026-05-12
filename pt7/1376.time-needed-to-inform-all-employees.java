import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;

/*
 * LeetCode 1376 - Time Needed to Inform All Employees
 */
class Solution {
    public int numOfMinutes(int n, int headID, int[] manager, int[] informTime) {
        List<List<Integer>> reports = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            reports.add(new ArrayList<>());
        }

        for (int employee = 0; employee < n; employee++) {
            if (manager[employee] != -1) {
                reports.get(manager[employee]).add(employee);
            }
        }

        int maxTime = 0;
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[] {headID, 0});

        while (!stack.isEmpty()) {
            int[] current = stack.pop();
            int employee = current[0];
            int elapsed = current[1];
            maxTime = Math.max(maxTime, elapsed);

            for (int report : reports.get(employee)) {
                stack.push(new int[] {report, elapsed + informTime[employee]});
            }
        }

        return maxTime;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * The manager array forms a rooted tree at headID. The time an employee hears
 * the news is the sum of inform times along the path from the head. Traverse
 * the tree and track the maximum elapsed time.
 *
 * Java data structures:
 * `List<List<Integer>>` is an adjacency list from manager to direct reports.
 * `ArrayDeque<int[]>` stores DFS states `[employee, elapsedTime]`.
 *
 * Edge cases:
 * - One employee returns 0.
 * - Managers with informTime 0 pass information without adding time.
 * - Iterative DFS avoids recursion-depth concerns.
 *
 * Complexity:
 * Time O(n), each employee is processed once.
 * Space O(n), for adjacency list and stack.
 */
