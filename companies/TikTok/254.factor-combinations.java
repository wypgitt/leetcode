import java.util.*;

/**
 * Algorithm:
 * Backtrack nondecreasing factors. For every factor that divides target, emit
 * path + factor + target/factor, then continue factoring target/factor starting
 * from the same factor.
 *
 * Complexity:
 * Output-dependent; recursion depth O(log n) in factor count.
 */
class Solution {
    private List<List<Integer>> ans;

    public List<List<Integer>> getFactors(int n) {
        ans = new ArrayList<>();
        dfs(2, n, new ArrayList<>());
        return ans;
    }

    private void dfs(int start, int target, List<Integer> path) {
        for (int factor = start; factor * factor <= target; factor++) {
            if (target % factor == 0) {
                List<Integer> combo = new ArrayList<>(path);
                combo.add(factor);
                combo.add(target / factor);
                ans.add(combo);

                path.add(factor);
                dfs(factor, target / factor, path);
                path.remove(path.size() - 1);
            }
        }
    }
}

