import java.util.*;

/**
 * Algorithm:
 * Sort the numbers. For each largest side nums[k], use two pointers to count
 * pairs (i, j) with nums[i] + nums[j] > nums[k]. When the condition holds,
 * every index from i through j - 1 also works with j.
 *
 * Complexity:
 * Time O(n^2), space O(1) beyond sorting.
 */
class Solution {
    public int triangleNumber(int[] nums) {
        Arrays.sort(nums);
        int ans = 0;
        for (int k = nums.length - 1; k >= 2; k--) {
            int i = 0;
            int j = k - 1;
            while (i < j) {
                if (nums[i] + nums[j] > nums[k]) {
                    ans += j - i;
                    j--;
                } else {
                    i++;
                }
            }
        }
        return ans;
    }
}

