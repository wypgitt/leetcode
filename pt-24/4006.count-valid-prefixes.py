#
# @lc app=leetcode id=4006 lang=python3
#
# [4006] Count Valid Prefixes
#
# https://leetcode.com/problems/count-valid-prefixes/description/
#
# algorithms
# Easy (77.73%)
# Likes:    30
# Dislikes: 1
# Total Accepted:    40.2K
# Total Submissions: 51.7K
# Testcase Example:  "\"00101\""
#
#
# You are given a binary string s.
#
# A prefix of s is considered valid if its characters can be rearranged to
# form an alternating string.
#
# Return the number of valid prefixes of s.
#
# A string is considered alternating if no two adjacent characters are
# equal.
#
# Example 1:
#
# Input: s = "00101"
#
# Output: 3
#
# Explanation:
#
# The valid prefixes are:
#
# "0": It is already an alternating string.
#
# "001": It can be rearranged into "010", which is an alternating string.
#
# "00101": It can be rearranged into "01010", which is an alternating
# string.
#
# Thus, the answer is 3.
#
# Example 2:
#
# Input: s = "101"
#
# Output: 3
#
# Explanation:
#
# All prefixes of s = "101" are already alternating strings. Thus, the
# answer is 3.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists only of '0' and '1'.
#

# @lc code=start
class Solution:
    def countValidPrefixes(self, s: str) -> int:
        """
        Interview explanation:
        A binary string rearranges to alternating iff the counts of 0 and 1
        differ by at most 1.

        Algorithm:
        - Track balance t = (#1) - (#0) over the prefix.
        - Prefix length L is valid iff |t| ≤ 1 (then majority can alternate).

        Complexity: O(n) time, O(1) space.
        """
        ans = t = 0
        for c in s:
            t += 1 if c == "1" else -1
            if abs(t) <= 1:
                ans += 1
        return ans
# @lc code=end
