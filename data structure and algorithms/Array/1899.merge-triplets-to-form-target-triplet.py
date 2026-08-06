#
# @lc app=leetcode id=1899 lang=python3
#
# [1899] Merge Triplets to Form Target Triplet
#
# https://leetcode.com/problems/merge-triplets-to-form-target-triplet/description/
#
# algorithms
# Medium (69.3%)
# Likes:    965
# Dislikes: 83
# Total Accepted:    128K
# Total Submissions: 184K
# Testcase Example:  "[[2,5,3],[1,8,4],[1,7,5]]"
#
# A triplet is an array of three integers. You are given a 2D integer array
# triplets, where triplets[i] = [a_i, b_i, c_i] describes the i^th triplet. You
# are also given an integer array target = [x, y, z] that describes the triplet
# you want to obtain.
#
# To obtain target, you may apply the following operation on triplets any
# number of times (possibly zero):
#
# Choose two indices (0-indexed) i and j (i != j) and update triplets[j] to
# become [max(a_i, a_j), max(b_i, b_j), max(c_i, c_j)].
#
# For example, if triplets[i] = [2, 5, 3] and triplets[j] = [1, 7, 5],
# triplets[j] will be updated to [max(2, 1), max(5, 7), max(3, 5)] = [2, 7, 5].
#
# Return true if it is possible to obtain the target triplet [x, y, z] as an
# element of triplets, or false otherwise.
#
# Example 1:
#
# Input: triplets = [[2,5,3],[1,8,4],[1,7,5]], target = [2,7,5]
# Output: true
# Explanation: Perform the following operations:
# - Choose the first and last triplets [[2,5,3],[1,8,4],[1,7,5]]. Update the
# last triplet to be [max(2,1), max(5,7), max(3,5)] = [2,7,5]. triplets =
# [[2,5,3],[1,8,4],[2,7,5]]
# The target triplet [2,7,5] is now an element of triplets.
#
# Example 2:
#
# Input: triplets = [[3,4,5],[4,5,6]], target = [3,2,5]
# Output: false
# Explanation: It is impossible to have [3,2,5] as an element because there is
# no 2 in any of the triplets.
#
# Example 3:
#
# Input: triplets = [[2,5,3],[2,3,4],[1,2,5],[5,2,3]], target = [5,5,5]
# Output: true
# Explanation: Perform the following operations:
# - Choose the first and third triplets [[2,5,3],[2,3,4],[1,2,5],[5,2,3]].
# Update the third triplet to be [max(2,1), max(5,2), max(3,5)] = [2,5,5].
# triplets = [[2,5,3],[2,3,4],[2,5,5],[5,2,3]].
# - Choose the third and fourth triplets [[2,5,3],[2,3,4],[2,5,5],[5,2,3]].
# Update the fourth triplet to be [max(2,5), max(5,2), max(5,3)] = [5,5,5].
# triplets = [[2,5,3],[2,3,4],[2,5,5],[5,5,5]].
# The target triplet [5,5,5] is now an element of triplets.
#
# Constraints:
#
# 1 <= triplets.length <= 10^5
#
# triplets[i].length == target.length == 3
#
# 1 <= a_i, b_i, c_i, x, y, z <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def mergeTriplets(self, triplets: List[List[int]], target: List[int]) -> bool:
        """
        Interview explanation:
        Update a working triplet by max with chosen triplets. Can we reach
        target? Never use a triplet that exceeds target in any coordinate;
        among the rest, check we can achieve each target coordinate.

        Algorithm:
        - Filter triplets with a≤x, b≤y, c≤z.
        - Return whether some filtered has a==x, some b==y, some c==z.

        Complexity: O(n) time, O(1) space.
        """
        x, y, z = target
        ax = ay = az = False
        for a, b, c in triplets:
            if a <= x and b <= y and c <= z:
                ax |= a == x
                ay |= b == y
                az |= c == z
        return ax and ay and az
# @lc code=end
