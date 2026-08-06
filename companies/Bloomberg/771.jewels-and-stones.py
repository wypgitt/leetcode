#
# @lc app=leetcode id=771 lang=python3
#
# [771] Jewels and Stones
#
# https://leetcode.com/problems/jewels-and-stones/description/
#
# algorithms
# Easy (89.63%)
# Likes:    5516
# Dislikes: 633
# Total Accepted:    1.4M
# Total Submissions: 1.6M
# Testcase Example:  "\"aA\""
#
# You're given strings jewels representing the types of stones that are jewels,
# and stones representing the stones you have. Each character in stones is a
# type of stone you have. You want to know how many of the stones you have are
# also jewels.
#
# Letters are case sensitive, so "a" is considered a different type of stone
# from "A".
#
# Example 1:
#
# Input: jewels = "aA", stones = "aAAbbbb"
# Output: 3
#
# Example 2:
#
# Input: jewels = "z", stones = "ZZ"
# Output: 0
#
# Constraints:
#
# 1 <= jewels.length, stones.length <= 50
#
# jewels and stones consist of only English letters.
#
# All the characters of jewels are unique.
#

# @lc code=start
class Solution:
    def numJewelsInStones(self, jewels: str, stones: str) -> int:
        """
        Interview explanation:
        Count how many stones are jewels. Put jewels in a set for O(1) lookup,
        then scan stones once.

        Algorithm:
        - jewel_set = set(jewels)
        - return sum(1 for c in stones if c in jewel_set)

        Complexity: O(|jewels| + |stones|) time, O(|jewels|) space.
        """
        jewel_set = set(jewels)
        return sum(1 for c in stones if c in jewel_set)
# @lc code=end

