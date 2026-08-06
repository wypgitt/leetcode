import java.util.*;

/**
 * Algorithm:
 * Sort numbers so duplicates are adjacent. During backtracking, skip nums[i]
 * when it equals nums[i - 1] and the previous equal value is not used in the
 * current prefix; otherwise the same permutation prefix would be generated.
 *
 * Complexity:
 * Time O(U * n), where U is the number of unique permutations. Space O(n)
 * excluding output.
 */
class Solution {
    private int[] nums;
    private boolean[] used;
    private List<Integer> path;
    private List<List<Integer>> ans;

    public List<List<Integer>> permuteUnique(int[] nums) {
        Arrays.sort(nums);
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
            if (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) {
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

