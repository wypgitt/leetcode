#
# @lc app=leetcode id=1090 lang=python3
#
# [1090] Largest Values From Labels
#
# https://leetcode.com/problems/largest-values-from-labels/description/
#
# algorithms
# Medium (64.54%)
# Likes:    503
# Dislikes: 639
# Total Accepted:    52.3K
# Total Submissions: 81.0K
# Testcase Example:  "[5,4,3,2,1]"
#
# You are given n item's value and label as two integer arrays values and
# labels. You are also given two integers numWanted and useLimit.
#
# Your task is to find a subset of items with the maximum sum of their values
# such that:
#
# The number of items is at most numWanted.
#
# The number of items with the same label is at most useLimit.
#
# Return the maximum sum.
#
# Example 1:
#
# Input: values = [5,4,3,2,1], labels = [1,1,2,2,3], numWanted = 3, useLimit =
# 1
#
# Output: 9
#
# Explanation:
#
# The subset chosen is the first, third, and fifth items with the sum of values
# 5 + 3 + 1.
#
# Example 2:
#
# Input: values = [5,4,3,2,1], labels = [1,3,3,3,2], numWanted = 3, useLimit =
# 2
#
# Output: 12
#
# Explanation:
#
# The subset chosen is the first, second, and third items with the sum of
# values 5 + 4 + 3.
#
# Example 3:
#
# Input: values = [9,8,8,7,6], labels = [0,0,0,1,1], numWanted = 3, useLimit =
# 1
#
# Output: 16
#
# Explanation:
#
# The subset chosen is the first and fourth items with the sum of values 9 + 7.
#
# Constraints:
#
# n == values.length == labels.length
#
# 1 <= n <= 2 * 10^4
#
# 0 <= values[i], labels[i] <= 2 * 10^4
#
# 1 <= numWanted, useLimit <= n
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def largestValsFromLabels(
        self, values: List[int], labels: List[int], numWanted: int, useLimit: int
    ) -> int:
        """
        Interview explanation:
        Greedy: take highest-value items first, skipping a label once it has
        been used useLimit times, until numWanted items taken.

        Algorithm (sort + count):
        - Sort (value, label) by value descending.
        - used[label] < useLimit and taken < numWanted → add value.

        Complexity: O(n log n) time, O(n) space for label counts.
        """
        items = sorted(zip(values, labels), reverse=True)
        used = defaultdict(int)
        total = taken = 0
        for val, lab in items:
            if taken == numWanted:
                break
            if used[lab] >= useLimit:
                continue
            used[lab] += 1
            total += val
            taken += 1
        return total
# @lc code=end
