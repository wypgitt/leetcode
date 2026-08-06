import java.util.*;

/**
 * Algorithm:
 * Backtrack increasing numbers from 1..9. Stop when k numbers are chosen, and
 * add the path only if the remaining sum is zero. Prune when a number exceeds
 * the remaining sum or not enough numbers remain.
 *
 * Complexity:
 * Time O(C(9,k) * k), recursion space O(k).
 */
class Solution {
    private int k;
    private List<Integer> path;
    private List<List<Integer>> ans;

    public List<List<Integer>> combinationSum3(int k, int n) {
        this.k = k;
        path = new ArrayList<>();
        ans = new ArrayList<>();
        dfs(1, n);
        return ans;
    }

    private void dfs(int start, int remaining) {
        if (path.size() == k) {
            if (remaining == 0) {
                ans.add(new ArrayList<>(path));
            }
            return;
        }
        int need = k - path.size();
        for (int num = start; num <= 9; num++) {
            if (num > remaining) {
                break;
            }
            if (10 - num < need) {
                break;
            }
            path.add(num);
            dfs(num + 1, remaining - num);
            path.remove(path.size() - 1);
        }
    }
}

