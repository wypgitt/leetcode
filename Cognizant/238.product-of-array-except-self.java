/**
 * Algorithm:
 * First pass writes prefix products before each index. Second pass multiplies
 * by suffix products after each index.
 *
 * Java data structures:
 * The output int[] stores prefix products and is updated in place with suffixes.
 *
 * Complexity:
 * Time O(n), extra space O(1) excluding output.
 */
class Solution {
    public int[] productExceptSelf(int[] nums) {
        int[] ans = new int[nums.length];
        int prefix = 1;
        for (int i = 0; i < nums.length; i++) {
            ans[i] = prefix;
            prefix *= nums[i];
        }
        int suffix = 1;
        for (int i = nums.length - 1; i >= 0; i--) {
            ans[i] *= suffix;
            suffix *= nums[i];
        }
        return ans;
    }
}

