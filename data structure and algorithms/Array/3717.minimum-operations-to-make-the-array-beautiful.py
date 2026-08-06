#
# @lc app=leetcode id=3717 lang=python3
#
# [3717] Minimum Operations to Make the Array Beautiful
#
# https://leetcode.com/problems/minimum-operations-to-make-the-array-beautiful/description/
#
# algorithms
# Medium (37.46%)
# Likes:    8
# Dislikes: 2
# Total Accepted:    393
# Total Submissions: 1K
# Testcase Example:  "[3,7,9]"
#
#
# You are given an integer array nums.
#
# An array is called beautiful if for every index i > 0, the value at
# nums[i] is divisible by nums[i - 1].
#
# In one operation, you may increment any element nums[i] (with i > 0) by
# 1.
#
# Return the minimum number of operations required to make the array
# beautiful.
#
# Example 1:
#
# Input: nums = [3,7,9]
#
# Output: 2
#
# Explanation:
#
# Applying the operation twice on nums[1] makes the array beautiful:
# [3,9,9]
#
# Example 2:
#
# Input: nums = [1,1,1]
#
# Output: 0
#
# Explanation:
#
# The given array is already beautiful.
#
# Example 3:
#
# Input: nums = [4]
#
# Output: 0
#
# Explanation:
#
# The array has only one element, so it's already beautiful.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 1 <= nums[i] <= 50​​​
#

# @lc code=start

from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        nums[i] must become a multiple of the previous chosen value; only later
        elements may increase. DP over possible previous values (small bound).

        Algorithm:
        - f[val] = min ops for the prefix ending with value val (nums[0] fixed).
        - For each next x, try multiples cur >= x of each previous val (cur <= 100),
          cost += cur - x; keep best per ending value.
        - Answer is min(f.values()).

        Complexity: O(n * V^2 / min_val) roughly with V ~ 100; tiny in practice.
        """
        f = {nums[0]: 0}
        for x in nums[1:]:
            g = {}
            for pre, s in f.items():
                cur = (x + pre - 1) // pre * pre
                while cur <= 100:
                    cost = s + cur - x
                    if cur not in g or g[cur] > cost:
                        g[cur] = cost
                    cur += pre
            f = g
        return min(f.values())
# @lc code=end
