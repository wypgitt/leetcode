import java.util.*;

/**
 * Algorithm:
 * Build edges from a poorer person to richer people. Memoized DFS returns the
 * quietest reachable richer-or-equal person for each node in the DAG.
 *
 * Java data structures:
 * ArrayList<Integer>[] is the adjacency list. int[] ans stores memoized
 * answers, using -1 as the uncomputed sentinel.
 *
 * Complexity:
 * Time O(n + e), space O(n + e).
 */
class Solution {
    private List<Integer>[] richerThan;
    private int[] quiet;
    private int[] ans;

    public int[] loudAndRich(int[][] richer, int[] quiet) {
        int n = quiet.length;
        this.quiet = quiet;
        richerThan = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            richerThan[i] = new ArrayList<>();
        }
        for (int[] edge : richer) {
            int rich = edge[0];
            int poor = edge[1];
            richerThan[poor].add(rich);
        }
        ans = new int[n];
        Arrays.fill(ans, -1);
        for (int person = 0; person < n; person++) {
            dfs(person);
        }
        return ans;
    }

    private int dfs(int person) {
        if (ans[person] != -1) {
            return ans[person];
        }
        int best = person;
        for (int rich : richerThan[person]) {
            int candidate = dfs(rich);
            if (quiet[candidate] < quiet[best]) {
                best = candidate;
            }
        }
        ans[person] = best;
        return best;
    }
}

