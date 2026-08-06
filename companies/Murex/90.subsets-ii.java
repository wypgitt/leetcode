import java.util.*;

/**
 * Algorithm:
 * Sort so duplicates are adjacent. During backtracking, skip nums[i] when it is
 * equal to nums[i - 1] and i is not the first choice at this recursion depth.
 *
 * Complexity:
 * Time O(U * n), where U is the number of unique subsets. Space O(n) recursion
 * excluding output.
 */
class Solution {
    private int[] nums;
    private List<Integer> path;
    private List<List<Integer>> ans;

    public List<List<Integer>> subsetsWithDup(int[] nums) {
        Arrays.sort(nums);
        this.nums = nums;
        path = new ArrayList<>();
        ans = new ArrayList<>();
        dfs(0);
        return ans;
    }

    private void dfs(int start) {
        ans.add(new ArrayList<>(path));
        for (int i = start; i < nums.length; i++) {
            if (i > start && nums[i] == nums[i - 1]) {
                continue;
            }
            path.add(nums[i]);
            dfs(i + 1);
            path.remove(path.size() - 1);
        }
    }
}

