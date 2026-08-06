#
# @lc app=leetcode id=696 lang=python3
#
# [696] Count Binary Substrings
#
# https://leetcode.com/problems/count-binary-substrings/description/
#
# algorithms
# Easy (70.53%)
# Likes:    4670
# Dislikes: 983
# Total Accepted:    384K
# Total Submissions: 544K
# Testcase Example:  "\"00110011\""
#
# Given a binary string s, return the number of non-empty substrings that have
# the same number of 0's and 1's, and all the 0's and all the 1's in these
# substrings are grouped consecutively.
#
# Substrings that occur multiple times are counted the number of times they
# occur.
#
# Example 1:
#
# Input: s = "00110011"
# Output: 6
# Explanation: There are 6 substrings that have equal number of consecutive 1's
# and 0's: "0011", "01", "1100", "10", "0011", and "01".
# Notice that some of these substrings repeat and are counted the number of
# times they occur.
# Also, "00110011" is not a valid substring because all the 0's (and 1's) are
# not grouped together.
#
# Example 2:
#
# Input: s = "10101"
# Output: 4
# Explanation: There are 4 substrings: "10", "01", "10", "01" that have equal
# number of consecutive 1's and 0's.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def countBinarySubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Count substrings with equal consecutive 0s and 1s (grouped). Between
        two adjacent groups of lengths a,b, contribute min(a,b) valid substrings.

        Algorithm:
        - Track prev group length and cur; on bit flip, add min(prev,cur), then
          prev,cur = cur,1; else cur++. Final add min(prev,cur).

        Complexity: O(n) time, O(1) space.
        """
        prev = cur = 0
        ans = 0
        for i, c in enumerate(s):
            if i == 0 or c != s[i - 1]:
                ans += min(prev, cur)
                prev, cur = cur, 1
            else:
                cur += 1
        ans += min(prev, cur)
        return ans
# @lc code=end
