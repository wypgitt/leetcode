import java.util.*;

/**
 * Algorithm:
 * Sort candidates, backtrack with each index used at most once, and skip
 * duplicate values at the same recursion depth so duplicate input values do not
 * produce duplicate combinations.
 *
 * Complexity:
 * Worst-case O(2^n * n) including output copies, space O(n) recursion.
 */
class Solution {
    private int[] candidates;
    private List<List<Integer>> ans;
    private List<Integer> path;

    public List<List<Integer>> combinationSum2(int[] candidates, int target) {
        Arrays.sort(candidates);
        this.candidates = candidates;
        ans = new ArrayList<>();
        path = new ArrayList<>();
        dfs(0, target);
        return ans;
    }

    private void dfs(int start, int remain) {
        if (remain == 0) {
            ans.add(new ArrayList<>(path));
            return;
        }
        Integer prev = null;
        for (int i = start; i < candidates.length; i++) {
            int val = candidates[i];
            if (prev != null && val == prev) {
                continue;
            }
            if (val > remain) {
                break;
            }
            path.add(val);
            dfs(i + 1, remain - val);
            path.remove(path.size() - 1);
            prev = val;
        }
    }
}

