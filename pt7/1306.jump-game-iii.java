import java.util.ArrayDeque;
import java.util.Deque;

/*
 * LeetCode 1306 - Jump Game III
 */
class Solution {
    public boolean canReach(int[] arr, int start) {
        boolean[] seen = new boolean[arr.length];
        Deque<Integer> stack = new ArrayDeque<>();
        stack.push(start);

        while (!stack.isEmpty()) {
            int index = stack.pop();
            if (index < 0 || index >= arr.length || seen[index]) {
                continue;
            }

            if (arr[index] == 0) {
                return true;
            }

            seen[index] = true;
            stack.push(index + arr[index]);
            stack.push(index - arr[index]);
        }

        return false;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Treat every array index as a graph node. From index i, the outgoing edges are
 * i + arr[i] and i - arr[i]. We run DFS from `start` and return true as soon as
 * we visit a node whose value is 0.
 *
 * Java data structures:
 * `ArrayDeque<Integer>` is used as a stack for iterative DFS. `boolean[] seen`
 * marks visited indices so cycles do not cause infinite looping.
 *
 * Edge cases:
 * - The start index already contains 0.
 * - A jump leaves the array; that candidate is ignored.
 * - Cycles such as jumping back and forth are stopped by `seen`.
 *
 * Complexity:
 * Time O(n), because every valid index is processed at most once.
 * Space O(n), for the visited array and DFS stack.
 */
