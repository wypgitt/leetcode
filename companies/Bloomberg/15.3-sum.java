import java.util.*;

/**
 * Algorithm:
 * Sort the array. Fix one unique anchor value, then use two pointers to find
 * pairs that complete sum zero. After outputting a triplet, skip duplicate
 * pointer values to avoid duplicate answers.
 *
 * Java data structures:
 * Arrays.sort orders the input in place; ArrayList stores triplets.
 *
 * Complexity:
 * Time O(n^2), extra space O(1) excluding output.
 */
class Solution {
    public List<List<Integer>> threeSum(int[] nums) {
        Arrays.sort(nums);
        List<List<Integer>> ans = new ArrayList<>();
        int n = nums.length;
        for (int i = 0; i < n - 2; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            if (nums[i] > 0) {
                break;
            }
            int left = i + 1;
            int right = n - 1;
            while (left < right) {
                int total = nums[i] + nums[left] + nums[right];
                if (total == 0) {
                    ans.add(Arrays.asList(nums[i], nums[left], nums[right]));
                    left++;
                    right--;
                    while (left < right && nums[left] == nums[left - 1]) {
                        left++;
                    }
                    while (left < right && nums[right] == nums[right + 1]) {
                        right--;
                    }
                } else if (total < 0) {
                    left++;
                } else {
                    right--;
                }
            }
        }
        return ans;
    }
}

