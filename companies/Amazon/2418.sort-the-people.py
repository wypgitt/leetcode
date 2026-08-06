#
# @lc app=leetcode id=2418 lang=python3
#
# [2418] Sort the People
#
# https://leetcode.com/problems/sort-the-people/description/
#
# algorithms
# Easy (84.81%)
# Likes:    1886
# Dislikes: 41
# Total Accepted:    395.1K
# Total Submissions: 465.9K
# Testcase Example:  "[\"Mary\",\"John\",\"Emma\"]\n[180,165,170]"
#
# You are given an array of strings names, and an array heights that consists of
# distinct positive integers. Both arrays are of length n.
#
# For each index i, names[i] and heights[i] denote the name and height of the
# i^th person.
#
# Return names sorted in descending order by the people's heights.
#
#
#
# Example 1:
#
# Input: names = ["Mary","John","Emma"], heights = [180,165,170]
# Output: ["Mary","Emma","John"]
# Explanation: Mary is the tallest, followed by Emma and John.
#
# Example 2:
#
# Input: names = ["Alice","Bob","Bob"], heights = [155,185,150]
# Output: ["Bob","Alice","Bob"]
# Explanation: The first Bob is the tallest, followed by Alice and the second
# Bob.
#
#
#
# Constraints:
#
#
# n == names.length == heights.length
#
#
# 1 <= n <= 10^3
#
#
# 1 <= names[i].length <= 20
#
#
# 1 <= heights[i] <= 10^5
#
#
# names[i] consists of lower and upper case English letters.
#
#
# All the values of heights are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def sortPeople(self, names: List[str], heights: List[int]) -> List[str]:
        """
        Interview explanation:
        Sort names by corresponding heights descending.

        Algorithm:
        - Pair and sort by height reverse; extract names.

        Complexity: O(n log n) time, O(n) space.
        """
        return [name for name, _ in sorted(zip(names, heights), key=lambda x: -x[1])]
# @lc code=end
