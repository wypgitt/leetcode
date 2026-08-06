#
# @lc app=leetcode id=2568 lang=python3
#
# [2568] Minimum Impossible OR
#
# https://leetcode.com/problems/minimum-impossible-or/description/
#
# algorithms
# Medium (59.33%)
# Likes:    389
# Dislikes: 22
# Total Accepted:    21.1K
# Total Submissions: 35.5K
# Testcase Example:  "[2,1]"
#
# You are given a 0-indexed integer array nums.
#
# We say that an integer x is expressible from nums if there exist some integers
# 0 <= index_1 < index_2 < ... < index_k < nums.length for which nums[index_1] |
# nums[index_2] | ... | nums[index_k] = x. In other words, an integer is
# expressible if it can be written as the bitwise OR of some subsequence of
# nums.
#
# Return the minimum positive non-zero integer that is not expressible from
# nums.
#
#
#
# Example 1:
#
# Input: nums = [2,1]
# Output: 4
# Explanation: 1 and 2 are already present in the array. We know that 3 is
# expressible, since nums[0] | nums[1] = 2 | 1 = 3. Since 4 is not expressible,
# we return 4.
#
# Example 2:
#
# Input: nums = [5,3,2]
# Output: 1
# Explanation: We can show that 1 is the smallest number that is not
# expressible.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def minImpossibleOR(self, nums: List[int]) -> int:
        """
        Interview explanation:
        The smallest positive integer that cannot be expressed as bitwise OR of any
        non-empty subset. Powers of two that are missing are the bottleneck.

        Algorithm:
        - Put nums in a set; return the smallest power of two not present.

        Complexity: O(n + log M) time, O(n) space.
        """
        s = set(nums)
        x = 1
        while x in s:
            x <<= 1
        return x

    def minImpossibleOR_bit(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same power-of-two scan using a bitset of present powers.

        Algorithm:
        - Collect powers of two from nums; find least unset bit position among powers.

        Complexity: O(n) time, O(1) space.
        """
        mask = 0
        for x in nums:
            if x & (x - 1) == 0:
                mask |= x
        ans = 1
        while mask & ans:
            ans <<= 1
        return ans
# @lc code=end
