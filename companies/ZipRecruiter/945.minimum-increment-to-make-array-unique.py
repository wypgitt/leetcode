#
# @lc app=leetcode id=945 lang=python3
#
# [945] Minimum Increment to Make Array Unique
#
# https://leetcode.com/problems/minimum-increment-to-make-array-unique/description/
#
# algorithms
# Medium (60.75%)
# Likes:    2798
# Dislikes: 86
# Total Accepted:    275K
# Total Submissions: 452K
# Testcase Example:  "[1,2,2]"
#
# You are given an integer array nums. In one move, you can pick an index i
# where 0 <= i < nums.length and increment nums[i] by 1.
#
# Return the minimum number of moves to make every value in nums unique.
#
# The test cases are generated so that the answer fits in a 32-bit integer.
#
# Example 1:
#
# Input: nums = [1,2,2]
# Output: 1
# Explanation: After 1 move, the array could be [1, 2, 3].
#
# Example 2:
#
# Input: nums = [3,2,1,2,1,7]
# Output: 6
# Explanation: After 6 moves, the array could be [3, 4, 1, 2, 5, 7].
# It can be shown that it is impossible for the array to have all unique values
# with 5 or less moves.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minIncrementForUnique(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Sort then greedily ensure each value is at least need = prev+1; moves
        = need - nums[i] when nums[i] < need.

        Algorithm (sort greedy):
        - Sort nums; need = nums[0]; ans=0 — actually start need from first
        - For each x in sorted: if x < need: ans += need-x; need += 1
          else need = x+1

        Complexity: O(n log n) time, O(1)/O(n) space depending on sort.
        """
        nums.sort()
        ans = 0
        need = nums[0]
        for x in nums:
            if x < need:
                ans += need - x
                need += 1
            else:
                need = x + 1
        return ans

    def minIncrementForUnique_counting(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: counting sort / frequency array over value range; walk
        values, carry duplicates forward to next slot.

        Algorithm:
        - freq up to max(nums)+len; walk v: if freq[v]>1: extra=freq[v]-1;
          freq[v+1]+=extra; ans+=extra

        Complexity: O(n + V) time, O(V) space.
        """
        if not nums:
            return 0
        mx = max(nums)
        freq = [0] * (mx + len(nums) + 1)
        for x in nums:
            freq[x] += 1
        ans = 0
        for v in range(len(freq) - 1):
            if freq[v] > 1:
                extra = freq[v] - 1
                freq[v + 1] += extra
                ans += extra
        return ans
# @lc code=end

