#
# @lc app=leetcode id=1221 lang=python3
#
# [1221] Split a String in Balanced Strings
#
# https://leetcode.com/problems/split-a-string-in-balanced-strings/description/
#
# algorithms
# Easy (87.55%)
# Likes:    2937
# Dislikes: 960
# Total Accepted:    401K
# Total Submissions: 458K
# Testcase Example:  "\"RLRRLLRLRL\""
#
# Balanced strings are those that have an equal quantity of 'L' and 'R'
# characters.
#
# Given a balanced string s, split it into some number of substrings such that:
#
# Each substring is balanced.
#
# Return the maximum number of balanced strings you can obtain.
#
# Example 1:
#
# Input: s = "RLRRLLRLRL"
# Output: 4
# Explanation: s can be split into "RL", "RRLL", "RL", "RL", each substring
# contains same number of 'L' and 'R'.
#
# Example 2:
#
# Input: s = "RLRRRLLRLL"
# Output: 2
# Explanation: s can be split into "RL", "RRRLLRLL", each substring contains
# same number of 'L' and 'R'.
# Note that s cannot be split into "RL", "RR", "RL", "LR", "LL", because the
# 2^nd and 5^th substrings are not balanced.
#
# Example 3:
#
# Input: s = "LLLLRRRR"
# Output: 1
# Explanation: s can be split into "LLLLRRRR".
#
# Constraints:
#
# 2 <= s.length <= 1000
#
# s[i] is either 'L' or 'R'.
#
# s is a balanced string.
#


# @lc code=start
class Solution:
    def balancedStringSplit(self, s: str) -> int:
        """
        Interview explanation:
        Split into maximum balanced strings (equal L and R). Greedy: maintain
        balance; each time it returns to 0, count one split.

        Algorithm:
        - bal=0, ans=0; for c: +1 L / -1 R; if bal==0 ans++

        Complexity: O(n) time, O(1) space.
        """
        bal = ans = 0
        for c in s:
            bal += 1 if c == 'L' else -1
            if bal == 0:
                ans += 1
        return ans
# @lc code=end
