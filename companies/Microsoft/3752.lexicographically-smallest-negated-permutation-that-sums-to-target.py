#
# @lc app=leetcode id=3752 lang=python3
#
# [3752] Lexicographically Smallest Negated Permutation that Sums to Target
#
# https://leetcode.com/problems/lexicographically-smallest-negated-permutation-that-sums-to-target/description/
#
# algorithms
# Medium (31.52%)
# Likes:    75
# Dislikes: 7
# Total Accepted:    14.2K
# Total Submissions: 45K
# Testcase Example:  "3\n0"
#
#
# You are given a positive integer n and an integer target.
#
# Return the lexicographically smallest array of integers of size n such
# that:
#
# The sum of its elements equals target.
#
# The absolute values of its elements form a permutation of size n.
#
# If no such array exists, return an empty array.
#
# A permutation of size n is a rearrangement of integers 1, 2, ..., n.
#
# Example 1:
#
# Input: n = 3, target = 0
#
# Output: [-3,1,2]
#
# Explanation:
#
# The arrays that sum to 0 and whose absolute values form a permutation of
# size 3 are:
#
# [-3, 1, 2]
#
# [-3, 2, 1]
#
# [-2, -1, 3]
#
# [-2, 3, -1]
#
# [-1, -2, 3]
#
# [-1, 3, -2]
#
# [1, -3, 2]
#
# [1, 2, -3]
#
# [2, -3, 1]
#
# [2, 1, -3]
#
# [3, -2, -1]
#
# [3, -1, -2]
#
# The lexicographically smallest one is [-3, 1, 2].
#
# Example 2:
#
# Input: n = 1, target = 10000000000
#
# Output: []
#
# Explanation:
#
# There are no arrays that sum to 10000000000 and whose absolute values
# form a permutation of size 1. Therefore, the answer is [].
#
# Constraints:
#
# 1 <= n <= 10^5
#
# -10^10 <= target <= 10^10
#

# @lc code=start
from typing import List


class Solution:
    def lexSmallestNegatedPerm(self, n: int, target: int) -> List[int]:
        """
        Interview explanation:
        Abs values are a permutation of 1..n with signs so the signed sum is
        target. Lex-smallest places large negatives as far left as possible and
        leftover positives ascending on the right.

        Algorithm:
        - Feasible iff |target| <= S = n(n+1)/2 and (S - target) even.
        - For i = n..1: negate i if target + i still reachable with 1..i-1;
          else take +i. Fill negatives left-to-right, positives right-to-left.

        Complexity: O(n) time, O(n) space.
        """
        total = n * (n + 1) // 2
        if abs(target) > total or (total - target) % 2:
            return []

        def reachable_max(m: int) -> int:
            return m * (m + 1) // 2

        result = [0] * n
        left, right = 0, n - 1
        for i in range(n, 0, -1):
            # Prefer -i when still reachable
            if target - (-i) <= reachable_max(i - 1):
                target -= -i
                result[left] = -i
                left += 1
            else:
                target -= i
                result[right] = i
                right -= 1
        return result
# @lc code=end
