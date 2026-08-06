#
# @lc app=leetcode id=952 lang=python3
#
# [952] Largest Component Size by Common Factor
#
# https://leetcode.com/problems/largest-component-size-by-common-factor/description/
#
# algorithms
# Hard (43.61%)
# Likes:    1744
# Dislikes: 95
# Total Accepted:    70.8K
# Total Submissions: 162K
# Testcase Example:  "[4,6,15,35]"
#
# You are given an integer array of unique positive integers nums. Consider the
# following graph:
#
# There are nums.length nodes, labeled nums[0] to nums[nums.length - 1],
#
# There is an undirected edge between nums[i] and nums[j] if nums[i] and
# nums[j] share a common factor greater than 1.
#
# Return the size of the largest connected component in the graph.
#
# Example 1:
#
# Input: nums = [4,6,15,35]
# Output: 4
#
# Example 2:
#
# Input: nums = [20,50,9,63]
# Output: 2
#
# Example 3:
#
# Input: nums = [2,3,6,7,4,12,21,39]
# Output: 8
#
# Constraints:
#
# 1 <= nums.length <= 2 * 10^4
#
# 1 <= nums[i] <= 10^5
#
# All the values of nums are unique.
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def largestComponentSize(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Connect numbers sharing a common factor > 1. Factorize each num and
        Union-Find union the number with each prime factor (or factors); largest
        component size among the nums is the answer.

        Algorithm (Union-Find + factorization):
        - UF on values up to max(nums)
        - For each x in nums: for each factor f of x (f>1): union(x, f)
        - Count find(x) frequencies for x in nums; return max

        Complexity: O(n * sqrt(M) * α(M)) time, O(M) space, M=max(nums).
        """
        m = max(nums)
        parent = list(range(m + 1))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        def factors(x: int):
            d = 2
            original = x
            while d * d <= x:
                if x % d == 0:
                    union(original, d)
                    while x % d == 0:
                        x //= d
                d += 1
            if x > 1:
                union(original, x)

        for x in nums:
            factors(x)

        return max(Counter(find(x) for x in nums).values())
# @lc code=end

