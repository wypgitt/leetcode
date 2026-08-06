#
# @lc app=leetcode id=3780 lang=python3
#
# [3780] Maximum Sum of Three Numbers Divisible by Three
#
# https://leetcode.com/problems/maximum-sum-of-three-numbers-divisible-by-three/description/
#
# algorithms
# Medium (47.62%)
# Likes:    65
# Dislikes: 1
# Total Accepted:    23.8K
# Total Submissions: 50.1K
# Testcase Example:  "[4,2,3,1]"
#
#
# You are given an integer array nums.
#
# Your task is to choose exactly three integers from nums such that their
# sum is divisible by three.
#
# Return the maximum possible sum of such a triplet. If no such triplet
# exists, return 0.
#
# Example 1:
#
# Input: nums = [4,2,3,1]
#
# Output: 9
#
# Explanation:
#
# The valid triplets whose sum is divisible by 3 are:
#
# (4, 2, 3) with a sum of 4 + 2 + 3 = 9.
#
# (2, 3, 1) with a sum of 2 + 3 + 1 = 6.
#
# Thus, the answer is 9.
#
# Example 2:
#
# Input: nums = [2,1,5]
#
# Output: 0
#
# Explanation:
#
# No triplet forms a sum divisible by 3, so the answer is 0.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maximumSum(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Triple sum ≡ 0 (mod 3) means residues (0,0,0), (1,1,1), (2,2,2), or (0,1,2).
        Keep the top three values per residue class.

        Algorithm:
        - Bucket by x%3; sort each desc.
        - Max among sum of top-3 in one class, or top-1 from each class.

        Complexity: O(n log n) time, O(n) space.
        """
        groups: List[List[int]] = [[], [], []]
        for x in nums:
            groups[x % 3].append(x)
        ans = 0
        for g in groups:
            g.sort(reverse=True)
            if len(g) >= 3:
                ans = max(ans, g[0] + g[1] + g[2])
        if groups[0] and groups[1] and groups[2]:
            ans = max(ans, groups[0][0] + groups[1][0] + groups[2][0])
        return ans

    def maximumSum_top3(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: maintain only top-3 per residue while scanning (O(1) memory).

        Algorithm:
        - Insert into size-3 descending arrays per residue; same candidate sums.

        Complexity: O(n) time, O(1) space.
        """
        def add(arr: List[int], x: int) -> None:
            arr.append(x)
            arr.sort(reverse=True)
            del arr[3:]

        groups: List[List[int]] = [[], [], []]
        for x in nums:
            add(groups[x % 3], x)
        ans = 0
        for g in groups:
            if len(g) == 3:
                ans = max(ans, sum(g))
        if all(groups):
            ans = max(ans, groups[0][0] + groups[1][0] + groups[2][0])
        return ans
# @lc code=end
