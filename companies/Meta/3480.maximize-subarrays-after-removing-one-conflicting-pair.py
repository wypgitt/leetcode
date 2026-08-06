#
# @lc app=leetcode id=3480 lang=python3
#
# [3480] Maximize Subarrays After Removing One Conflicting Pair
#
# https://leetcode.com/problems/maximize-subarrays-after-removing-one-conflicting-pair/description/
#
# algorithms
# Hard (64.48%)
# Likes:    309
# Dislikes: 57
# Total Accepted:    57.8K
# Total Submissions: 89.7K
# Testcase Example:  "4\n[[2,3],[1,4]]"
#
#
# You are given an integer n which represents an array nums containing the
# numbers from 1 to n in order. Additionally, you are given a 2D array
# conflictingPairs, where conflictingPairs[i] = [a, b] indicates that a
# and b form a conflicting pair.
#
# Remove exactly one element from conflictingPairs. Afterward, count the
# number of non-empty subarrays of nums which do not contain both a and b
# for any remaining conflicting pair [a, b].
#
# Return the maximum number of subarrays possible after removing exactly
# one conflicting pair.
#
# Example 1:
#
# Input: n = 4, conflictingPairs = [[2,3],[1,4]]
#
# Output: 9
#
# Explanation:
#
# Remove [2, 3] from conflictingPairs. Now, conflictingPairs = [[1, 4]].
#
# There are 9 subarrays in nums where [1, 4] do not appear together. They
# are [1], [2], [3], [4], [1, 2], [2, 3], [3, 4], [1, 2, 3] and [2, 3, 4].
#
# The maximum number of subarrays we can achieve after removing one
# element from conflictingPairs is 9.
#
# Example 2:
#
# Input: n = 5, conflictingPairs = [[1,2],[2,5],[3,5]]
#
# Output: 12
#
# Explanation:
#
# Remove [1, 2] from conflictingPairs. Now, conflictingPairs = [[2, 5],
# [3, 5]].
#
# There are 12 subarrays in nums where [2, 5] and [3, 5] do not appear
# together.
#
# The maximum number of subarrays we can achieve after removing one
# element from conflictingPairs is 12.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# 1 <= conflictingPairs.length <= 2 * n
#
# conflictingPairs[i].length == 2
#
# 1 <= conflictingPairs[i][j] <= n
#
# conflictingPairs[i][0] != conflictingPairs[i][1]
#

# @lc code=start
from typing import List


class Solution:
    def maxSubarrays(self, n: int, conflictingPairs: List[List[int]]) -> int:
        """
        Interview explanation:
        A subarray ending at `right` is valid iff its left start is > the
        strongest conflict left endpoint among pairs with right endpoint
        <= right. Removing the binding conflict gains the gap to the second
        strongest left.

        Algorithm:
        - Group each pair as conflicts[max] <- min.
        - Sweep right=1..n maintaining maxLeft and secondMaxLeft.
        - Base valid count += right - maxLeft.
        - gains[maxLeft] += maxLeft - secondMaxLeft.
        - Answer = base + max(gains).

        Complexity: O(n + P) time, O(n + P) space.
        """
        conflicts: List[List[int]] = [[] for _ in range(n + 1)]
        for a, b in conflictingPairs:
            conflicts[max(a, b)].append(min(a, b))

        gains = [0] * (n + 1)
        valid = 0
        max_left = 0
        second_max_left = 0
        for right in range(1, n + 1):
            for left in conflicts[right]:
                if left > max_left:
                    second_max_left, max_left = max_left, left
                elif left > second_max_left:
                    second_max_left = left
            valid += right - max_left
            gains[max_left] += max_left - second_max_left
        return valid + max(gains)
# @lc code=end

