/*
 * @lc app=leetcode id=3889 lang=java
 *
 * [3889] Mirror Frequency Distance
 *
 * Count characters, then compare mirrored lowercase letters a/z, b/y, ...
 * and mirrored digits 0/9, 1/8, ... . Sum absolute frequency differences.
 *
 * Time: O(|s| + alphabet). Space: O(alphabet).
 */

// @lc code=start
class Solution {
    public int mirrorFrequency(String s) {
        int[] freq = new int[128];
        for (int i = 0; i < s.length(); i++) {
            freq[s.charAt(i)]++;
        }

        int answer = 0;
        for (int offset = 0; offset < 13; offset++) {
            answer += Math.abs(freq['a' + offset] - freq['z' - offset]);
        }
        for (int offset = 0; offset < 5; offset++) {
            answer += Math.abs(freq['0' + offset] - freq['9' - offset]);
        }
        return answer;
    }
}
// @lc code=end
