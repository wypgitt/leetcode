/**
 * Algorithm:
 * Dynamic programming over endpoints. lengths[i] is the longest increasing
 * subsequence ending at i; counts[i] is how many such sequences exist. Extend
 * from every j < i with nums[j] < nums[i].
 *
 * Java data structures:
 * Two int arrays store lengths and counts.
 *
 * Complexity:
 * Time O(n^2), space O(n).
 */
class Solution {
    public int findNumberOfLIS(int[] nums) {
        int n = nums.length;
        int[] lengths = new int[n];
        int[] counts = new int[n];
        int longest = 0;
        int ans = 0;

        for (int i = 0; i < n; i++) {
            lengths[i] = 1;
            counts[i] = 1;
            for (int j = 0; j < i; j++) {
                if (nums[j] < nums[i]) {
                    if (lengths[j] + 1 > lengths[i]) {
                        lengths[i] = lengths[j] + 1;
                        counts[i] = counts[j];
                    } else if (lengths[j] + 1 == lengths[i]) {
                        counts[i] += counts[j];
                    }
                }
            }
            if (lengths[i] > longest) {
                longest = lengths[i];
                ans = counts[i];
            } else if (lengths[i] == longest) {
                ans += counts[i];
            }
        }
        return ans;
    }
}

