#
# @lc app=leetcode id=2703 lang=python3
#
# [2703] Return Length of Arguments Passed
#
# https://leetcode.com/problems/return-length-of-arguments-passed/description/
#
# algorithms
# Easy (94.44%)
# Likes:    432
# Dislikes: 177
# Total Accepted:    313.2K
# Total Submissions: 331.6K
# Testcase Example:  "[5]"
#
# Write a function argumentsLength that returns the count of arguments passed to
# it.
#
#
#
# Example 1:
#
# Input: args = [5]
# Output: 1
# Explanation:
# argumentsLength(5); // 1
#
# One value was passed to the function so it should return 1.
#
# Example 2:
#
# Input: args = [{}, null, "3"]
# Output: 3
# Explanation:
# argumentsLength({}, null, "3"); // 3
#
# Three values were passed to the function so it should return 3.
#
#
#
# Constraints:
#
#
# args is a valid JSON array
#
#
# 0 <= args.length <= 100
#

# @lc code=start
from typing import Any


class Solution:
    def argumentsLength(self, *args: Any) -> int:
        """
        Interview explanation:
        JavaScript problem (Python analog): return how many arguments were passed.

        Algorithm:
        - Return len(args).

        Complexity: O(1) time, O(1) space.
        """
        return len(args)
# @lc code=end
