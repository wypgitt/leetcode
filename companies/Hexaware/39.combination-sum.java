import java.util.*;

/**
 * Algorithm:
 * Sort candidates and backtrack over nondecreasing choices. Reuse is allowed,
 * so the recursive call keeps the same start index. Stop the loop when the
 * candidate exceeds the remaining sum.
 *
 * Java data structures:
 * ArrayList<Integer> is the mutable path; answers copy it when remain == 0.
 *
 * Complexity:
 * Exponential in the number of valid combinations; recursion depth is at most
 * target / min(candidates), excluding output.
 */
class Solution {
    private int[] candidates;
    private List<List<Integer>> ans;
    private List<Integer> path;

    public List<List<Integer>> combinationSum(int[] candidates, int target) {
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
        for (int i = start; i < candidates.length; i++) {
            int val = candidates[i];
            if (val > remain) {
                break;
            }
            path.add(val);
            dfs(i, remain - val);
            path.remove(path.size() - 1);
        }
    }
}

