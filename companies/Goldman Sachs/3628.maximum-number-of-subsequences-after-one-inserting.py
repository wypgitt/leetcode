#
# @lc app=leetcode id=3628 lang=python3
#
# [3628] Maximum Number of Subsequences After One Inserting
#
# https://leetcode.com/problems/maximum-number-of-subsequences-after-one-inserting/description/
#
# algorithms
# Medium (32.21%)
# Likes:    143
# Dislikes: 5
# Total Accepted:    31.8K
# Total Submissions: 98.9K
# Testcase Example:  "\"LMCT\""
#
#
# You are given a string s consisting of uppercase English letters.
#
# You are allowed to insert at most one uppercase English letter at any
# position (including the beginning or end) of the string.
#
# Return the maximum number of "LCT" subsequences that can be formed in
# the resulting string after at most one insertion.
#
# Example 1:
#
# Input: s = "LMCT"
#
# Output: 2
#
# Explanation:
#
# We can insert a "L" at the beginning of the string s to make "LLMCT",
# which has 2 subsequences, at indices [0, 3, 4] and [1, 3, 4].
#
# Example 2:
#
# Input: s = "LCCT"
#
# Output: 4
#
# Explanation:
#
# We can insert a "L" at the beginning of the string s to make "LLCCT",
# which has 4 subsequences, at indices [0, 2, 4], [0, 3, 4], [1, 2, 4] and
# [1, 3, 4].
#
# Example 3:
#
# Input: s = "L"
#
# Output: 0
#
# Explanation:
#
# Since it is not possible to obtain the subsequence "LCT" by inserting a
# single letter, the result is 0.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of uppercase English letters.
#

# @lc code=start

class Solution:
    def numOfSubsequences(self, s: str) -> int:
        """
        Interview explanation:
        Maximize "LCT" subsequences after inserting at most one letter L/C/T.
        Base count plus the best single-letter gain.

        Algorithm:
        - Scan left-to-right tracking #L, #LC, #LCT and remaining #T.
        - Gain(insert L) = total CT pairs; gain(insert T) = total LC pairs;
          gain(insert C) = max over positions of (#L left)*(#T right).
        - Answer = LCT + max of those three gains.

        Complexity: O(n) time, O(1) space.
        """
        cnt_l = cnt_c = 0
        cnt_t = s.count("T")
        mx_lt = cnt_lct = cnt_lc = cnt_ct = 0
        for ch in s:
            mx_lt = max(mx_lt, cnt_l * cnt_t)
            if ch == "L":
                cnt_l += 1
            elif ch == "C":
                cnt_c += 1
                cnt_lc += cnt_l
            elif ch == "T":
                cnt_t -= 1
                cnt_ct += cnt_c
                cnt_lct += cnt_lc
        return cnt_lct + max(cnt_ct, mx_lt, cnt_lc)
# @lc code=end

