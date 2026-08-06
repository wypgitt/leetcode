#
# @lc app=leetcode id=3595 lang=python3
#
# [3595] Once Twice
#
# https://leetcode.com/problems/once-twice/description/
#
# algorithms
# Medium (76.13%)
# Likes:    9
# Dislikes: 3
# Total Accepted:    727
# Total Submissions: 955
# Testcase Example:  "[2,2,3,2,5,5,5,7,7]"
#
#
# You are given an integer array nums. In this array:
#
# Exactly one element appears once.
#
# Exactly one element appears twice.
#
# All other elements appear exactly three times.
#
# Return an integer array of length 2, where the first element is the one
# that appears once, and the second is the one that appears twice.
#
# Your solution must run in O(n) time and O(1) space.
#
# Example 1:
#
# Input: nums = [2,2,3,2,5,5,5,7,7]
#
# Output: [3,7]
#
# Explanation:
#
# The element 3 appears once, and the element 7 appears twice. The
# remaining elements each appear three times.
#
# Example 2:
#
# Input: nums = [4,4,6,4,9,9,9,6,8]
#
# Output: [8,6]
#
# Explanation:
#
# The element 8 appears once, and the element 6 appears twice. The
# remaining elements each appear three times.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# -2^31 <= nums[i] <= 2^31 - 1
#
# nums.length is a multiple of 3.
#
# Exactly one element appears once, one element appears twice, and all
# other elements appear three times.
#

# @lc code=start

from typing import List


class Solution:
    def onceTwice(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        All values appear 3× except one once and one twice. Bit-parallel mod-3
        counters isolate bits unique to the once/twice numbers; a second filtered
        pass recovers the once value, then the twice value.

        Algorithm:
        - dp[r] = bitmask of positions whose count ≡ r (mod 3).
        - dp[1] = once-only bits, dp[2] = twice-only bits.
        - Rescan numbers compatible with the once pattern; mod-3 again → once.
        - twice = (once ^ once_only_bits) | twice_only_bits.

        Complexity: O(n) time, O(1) space.
        """
        dp = [0, 0, 0]
        dp[0] = ~0
        for x in nums:
            dp = [(x & dp[i - 1]) | (~x & dp[i]) for i in range(3)]

        dp2 = [0, 0, 0]
        dp2[0] = ~0
        for x in nums:
            if (~x & dp[1]) or (x & dp[2]):
                continue
            dp2 = [(x & dp2[i - 1]) | (~x & dp2[i]) for i in range(3)]

        once = dp2[1]
        twice = (once ^ dp[1]) | dp[2]
        return [once, twice]
# @lc code=end
