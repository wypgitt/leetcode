/*
 * @lc app=leetcode id=3895 lang=java
 *
 * [3895] Count Digit Appearances
 *
 * Mirror the Python reference directly: convert each number to a string and
 * count occurrences of the requested digit.
 *
 * Time: O(total digits). Space: O(1) excluding temporary strings.
 */

// @lc code=start
class Solution {
    public int countDigitOccurrences(int[] nums, int digit) {
        char target = (char) ('0' + digit);
        int answer = 0;
        for (int number : nums) {
            String text = Integer.toString(number);
            for (int i = 0; i < text.length(); i++) {
                if (text.charAt(i) == target) {
                    answer++;
                }
            }
        }
        return answer;
    }
}
// @lc code=end
