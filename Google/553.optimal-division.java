/**
 * Algorithm:
 * To maximize a / b / c / d..., keep nums[0] as the numerator and minimize the
 * denominator by grouping every remaining number as nums[1] / nums[2] / ...
 * Thus the optimal expression is nums[0] / (nums[1] / nums[2] / ...).
 *
 * Complexity:
 * Time O(n) to build the expression, space O(n) for the output string.
 */
class Solution {
    public String optimalDivision(int[] nums) {
        if (nums.length == 1) {
            return String.valueOf(nums[0]);
        }
        if (nums.length == 2) {
            return nums[0] + "/" + nums[1];
        }
        StringBuilder ans = new StringBuilder();
        ans.append(nums[0]).append("/(").append(nums[1]);
        for (int i = 2; i < nums.length; i++) {
            ans.append('/').append(nums[i]);
        }
        ans.append(')');
        return ans.toString();
    }
}

