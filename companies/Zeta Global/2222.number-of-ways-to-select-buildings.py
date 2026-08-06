#
# @lc app=leetcode id=2222 lang=python3
#
# [2222] Number of Ways to Select Buildings
#
# https://leetcode.com/problems/number-of-ways-to-select-buildings/description/
#
# algorithms
# Medium (50.95%)
# Likes:    1069
# Dislikes: 54
# Total Accepted:    55.4K
# Total Submissions: 108.7K
# Testcase Example:  "\"001101\""
#
# You are given a 0-indexed binary string s which represents the types of
# buildings along a street where:
#
#
# s[i] = '0' denotes that the i^th building is an office and
#
#
# s[i] = '1' denotes that the i^th building is a restaurant.
#
# As a city official, you would like to select 3 buildings for random
# inspection. However, to ensure variety, no two consecutive buildings out of
# the selected buildings can be of the same type.
#
#
# For example, given s = "001101", we cannot select the 1^st, 3^rd, and 5^th
# buildings as that would form "011" which is not allowed due to having two
# consecutive buildings of the same type.
#
# Return the number of valid ways to select 3 buildings.
#
#
#
# Example 1:
#
# Input: s = "001101"
# Output: 6
# Explanation:
# The following sets of indices selected are valid:
# - [0,2,4] from "001101" forms "010"
# - [0,3,4] from "001101" forms "010"
# - [1,2,4] from "001101" forms "010"
# - [1,3,4] from "001101" forms "010"
# - [2,4,5] from "001101" forms "101"
# - [3,4,5] from "001101" forms "101"
# No other selection is valid. Thus, there are 6 total ways.
#
# Example 2:
#
# Input: s = "11100"
# Output: 0
# Explanation: It can be shown that there are no valid selections.
#
#
#
# Constraints:
#
#
# 3 <= s.length <= 10^5
#
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def numberOfWays(self, s: str) -> int:
        """
        Interview explanation:
        Count subsequences of length 3 with alternating office/restaurant:
        "010" or "101".

        Algorithm:
        - Prefix counts of 0/1; for each middle index, left_opposite * right_opposite.

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        total0 = s.count("0")
        total1 = n - total0
        left0 = left1 = 0
        ans = 0
        for ch in s:
            if ch == "0":
                # middle 0 contributes left1 * right1 for pattern 101
                right1 = total1 - left1
                ans += left1 * right1
                left0 += 1
            else:
                right0 = total0 - left0
                ans += left0 * right0
                left1 += 1
        return ans
# @lc code=end
