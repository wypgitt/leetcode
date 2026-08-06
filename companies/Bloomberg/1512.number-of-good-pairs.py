#
# @lc app=leetcode id=1512 lang=python3
#
# [1512] Number of Good Pairs
#
# https://leetcode.com/problems/number-of-good-pairs/description/
#
# algorithms
# Easy (89.9%)
# Likes:    5910
# Dislikes: 286
# Total Accepted:    1.1M
# Total Submissions: 1.2M
# Testcase Example:  "[1,2,3,1,1,3]"
#
# Given an array of integers nums, return the number of good pairs.
#
# A pair (i, j) is called good if nums[i] == nums[j] and i < j.
#
# Example 1:
#
# Input: nums = [1,2,3,1,1,3]
# Output: 4
# Explanation: There are 4 good pairs (0,3), (0,4), (3,4), (2,5) 0-indexed.
#
# Example 2:
#
# Input: nums = [1,1,1,1]
# Output: 6
# Explanation: Each pair in the array are good.
#
# Example 3:
#
# Input: nums = [1,2,3]
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 100
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def numIdenticalPairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Good pair: i<j and nums[i]==nums[j]. For frequency f of a value,
        pairs = C(f,2)=f*(f-1)/2. Count frequencies and sum.

        Algorithm:
        - Counter; ans += f*(f-1)//2 for each f (or accumulate while scanning).

        Complexity: O(n) time, O(U) space.
        """
        ans = 0
        seen: dict[int, int] = {}
        for x in nums:
            ans += seen.get(x, 0)
            seen[x] = seen.get(x, 0) + 1
        return ans

    def numIdenticalPairs_counter(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: full Counter then C(f,2) for each value.

        Algorithm:
        - Counter; sum f*(f-1)//2.

        Complexity: O(n) time, O(U) space.
        """
        return sum(f * (f - 1) // 2 for f in Counter(nums).values())
# @lc code=end
