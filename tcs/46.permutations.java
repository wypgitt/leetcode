import java.util.*;

/**
 * Algorithm:
 * Backtrack by choosing one unused number for each position. A boolean used
 * array gives O(1) membership checks for the current path.
 *
 * Complexity:
 * Time O(n! * n), space O(n) excluding output.
 */
class Solution {
    private int[] nums;
    private boolean[] used;
    private List<Integer> path;
    private List<List<Integer>> ans;

    public List<List<Integer>> permute(int[] nums) {
        this.nums = nums;
        used = new boolean[nums.length];
        path = new ArrayList<>();
        ans = new ArrayList<>();
        dfs();
        return ans;
    }

    private void dfs() {
        if (path.size() == nums.length) {
            ans.add(new ArrayList<>(path));
            return;
        }
        for (int i = 0; i < nums.length; i++) {
            if (used[i]) {
                continue;
            }
            used[i] = true;
            path.add(nums[i]);
            dfs();
            path.remove(path.size() - 1);
            used[i] = false;
        }
    }
}

