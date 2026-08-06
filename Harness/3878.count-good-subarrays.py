#
# @lc app=leetcode id=3878 lang=python3
#
# [3878] Count Good Subarrays
#
# https://leetcode.com/problems/count-good-subarrays/description/
#
# algorithms
# Hard (25.79%)
# Likes:    85
# Dislikes: 2
# Total Accepted:    7.3K
# Total Submissions: 28.4K
# Testcase Example:  "[4,2,3]"
#
#
# You are given an integer array nums.
#
# A subarray is called good if the bitwise OR of all its elements is equal
# to at least one element present in that subarray.
#
# Return the number of good subarrays in nums.
#
# Here, the bitwise OR of two integers a and b is denoted by a | b.
#
# Example 1:
#
# Input: nums = [4,2,3]
#
# Output: 4
#
# Explanation:
#
# The subarrays of nums are:
#
#                         Subarray
#                         Bitwise OR
#                         Present in Subarray
#
#                         [4]
#                         4 = 4
#                         Yes
#
#                         [2]
#                         2 = 2
#                         Yes
#
#                         [3]
#                         3 = 3
#                         Yes
#
#                         [4, 2]
#                         4 | 2 = 6
#                         No
#
#                         [2, 3]
#                         2 | 3 = 3
#                         Yes
#
#                         [4, 2, 3]
#                         4 | 2 | 3 = 7
#                         No
#
# Thus, the good subarrays of nums are [4], [2], [3] and [2, 3]. Thus, the
# answer is 4.
#
# Example 2:
#
# Input: nums = [1,3,1]
#
# Output: 6
#
# Explanation:
#
# Any subarray of nums containing 3 has bitwise OR equal to 3, and
# subarrays containing only 1 have bitwise OR equal to 1.
#
# In both cases, the result is present in the subarray, so all subarrays
# are good, and the answer is 6.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
class Solution:
    def countGoodSubarrays(self, nums: list[int]) -> int:
        """
        Interview explanation:
        A subarray is good iff its OR equals some element inside it. Count
        subarrays whose OR equals nums[i], attributing each to one index.

        Algorithm:
        - For OR = nums[i], every element must be a bit-subset of nums[i].
        - Monotonic stack: left/right bounds where that holds; use strict < on
          the left so equal OR values are not double-counted.
        - Add (i - l[i]) * (r[i] - i) for each i.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums)
        l = [-1] * n
        stk: list[int] = []
        for i, x in enumerate(nums):
            while stk and nums[stk[-1]] < x and (nums[stk[-1]] | x) == x:
                stk.pop()
            l[i] = stk[-1] if stk else -1
            stk.append(i)
        r = [n] * n
        stk = []
        for i in range(n - 1, -1, -1):
            while stk and (nums[stk[-1]] | nums[i]) == nums[i]:
                stk.pop()
            r[i] = stk[-1] if stk else n
            stk.append(i)
        return sum((i - l[i]) * (r[i] - i) for i in range(n))
# @lc code=end
