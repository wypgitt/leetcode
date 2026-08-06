import java.util.*;

/**
 * Algorithm:
 * Sort the array, fix two unique indices, and solve the remaining 2Sum with
 * two pointers. Skip duplicates at every layer.
 *
 * Java data structures:
 * Arrays.sort orders the input; ArrayList stores quadruplets. long is used for
 * the sum to avoid Java int overflow on large values.
 *
 * Complexity:
 * Time O(n^3), extra space O(1) excluding output.
 */
class Solution {
    public List<List<Integer>> fourSum(int[] nums, int target) {
        Arrays.sort(nums);
        List<List<Integer>> ans = new ArrayList<>();
        int n = nums.length;
        for (int i = 0; i < n - 3; i++) {
            if (i > 0 && nums[i] == nums[i - 1]) {
                continue;
            }
            for (int j = i + 1; j < n - 2; j++) {
                if (j > i + 1 && nums[j] == nums[j - 1]) {
                    continue;
                }
                int left = j + 1;
                int right = n - 1;
                while (left < right) {
                    long total = (long) nums[i] + nums[j] + nums[left] + nums[right];
                    if (total == target) {
                        ans.add(Arrays.asList(nums[i], nums[j], nums[left], nums[right]));
                        left++;
                        right--;
                        while (left < right && nums[left] == nums[left - 1]) {
                            left++;
                        }
                        while (left < right && nums[right] == nums[right + 1]) {
                            right--;
                        }
                    } else if (total < target) {
                        left++;
                    } else {
                        right--;
                    }
                }
            }
        }
        return ans;
    }
}

