/*
 * @lc app=leetcode id=3876 lang=java
 *
 * [3876] Construct Uniform Parity Array II
 *
 * If all values already have the same parity, success is immediate. Otherwise,
 * the Python logic checks whether the smallest odd value is smaller than the
 * smallest even value.
 *
 * Time: O(n). Space: O(1).
 */

// @lc code=start
class Solution {
    public boolean uniformArray(int[] nums1) {
        int minOdd = Integer.MAX_VALUE;
        int minEven = Integer.MAX_VALUE;

        for (int value : nums1) {
            if ((value & 1) == 1) {
                minOdd = Math.min(minOdd, value);
            } else {
                minEven = Math.min(minEven, value);
            }
        }
        if (minOdd == Integer.MAX_VALUE || minEven == Integer.MAX_VALUE) {
            return true;
        }
        return minOdd < minEven;
    }
}
// @lc code=end
