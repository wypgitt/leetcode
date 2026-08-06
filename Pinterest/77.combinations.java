import java.util.*;

/**
 * Algorithm:
 * Backtrack combinations in increasing order. The start value prevents
 * duplicate orderings, and the loop bound prunes branches with too few numbers
 * remaining to complete k values.
 *
 * Complexity:
 * Time O(C(n,k) * k), recursion space O(k), plus output.
 */
class Solution {
    private int n;
    private int k;
    private List<Integer> path;
    private List<List<Integer>> ans;

    public List<List<Integer>> combine(int n, int k) {
        this.n = n;
        this.k = k;
        path = new ArrayList<>();
        ans = new ArrayList<>();
        dfs(1);
        return ans;
    }

    private void dfs(int start) {
        if (path.size() == k) {
            ans.add(new ArrayList<>(path));
            return;
        }
        int need = k - path.size();
        for (int value = start; value <= n - need + 1; value++) {
            path.add(value);
            dfs(value + 1);
            path.remove(path.size() - 1);
        }
    }
}

