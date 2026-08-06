#
# @lc app=leetcode id=2936 lang=python3
#
# [2936] Number of Equal Numbers Blocks
#
# https://leetcode.com/problems/number-of-equal-numbers-blocks/description/
#
# algorithms
# Medium (62.58%)
# Likes:    24
# Dislikes: 8
# Total Accepted:    2.5K
# Total Submissions: 4K
# Testcase Example:  "[3,3,3,3,3]"
#
#
# You are given a 0-indexed array of integers, nums. The following
# property holds for nums:
#
# All occurrences of a value are adjacent. In other words, if there are
# two indices i < j such that nums[i] == nums[j], then for every index k
# that i < k < j, nums[k] == nums[i].
#
# Since nums is a very large array, you are given an instance of the class
# BigArray which has the following functions:
#
# int at(long long index): Returns the value of nums[i].
#
# void size(): Returns nums.length.
#
# Let's partition the array into maximal blocks such that each block
# contains equal values. Return the number of these blocks.
#
# Note that if you want to test your solution using a custom test,
# behavior for tests with nums.length > 10 is undefined.
#
# Example 1:
#
# Input: nums = [3,3,3,3,3]
# Output: 1
# Explanation: There is only one block here which is the whole array
# (because all numbers are equal) and that is: [3,3,3,3,3]. So the answer
# would be 1.
#
# Example 2:
#
# Input: nums = [1,1,1,3,9,9,9,2,10,10]
# Output: 5
# Explanation: There are 5 blocks here:
# Block number 1: [1,1,1,3,9,9,9,2,10,10]
# Block number 2: [1,1,1,3,9,9,9,2,10,10]
# Block number 3: [1,1,1,3,9,9,9,2,10,10]
# Block number 4: [1,1,1,3,9,9,9,2,10,10]
# Block number 5: [1,1,1,3,9,9,9,2,10,10]
# So the answer would be 5.
#
# Example 3:
#
# Input: nums = [1,2,3,4,5,6,7]
# Output: 7
# Explanation: Since all numbers are distinct, there are 7 blocks here and
# each element representing one block. So the answer would be 7.
#
# Constraints:
#
# 1 <= nums.length <= 10^15
#
# 1 <= nums[i] <= 10^9
#
# The input is generated such that all equal values are adjacent.
#
# The sum of the elements of nums is at most 10^15.
#
# @lc code=start

from typing import Optional

# Definition for BigArray.
# class BigArray:
#     def at(self, index: int) -> int:
#         pass
#     def size(self) -> int:
#         pass


try:
    BigArray  # type: ignore[name-defined]
except NameError:

    class BigArray:  # type: ignore[no-redef]
        def at(self, index: int) -> int:
            return 0

        def size(self) -> int:
            return 0


class Solution:
    def countBlocks(self, nums: Optional["BigArray"]) -> int:
        """
        Interview explanation:
        Premium: nums via BigArray (length up to 1e15) with equal values contiguous.
        Count maximal constant blocks without scanning linearly.

        Algorithm:
        - For each block start i, binary search first index with a different value.

        Complexity: O(m log n) time (m = #blocks), O(1) space.
        """
        n = nums.size()
        i = ans = 0
        while i < n:
            ans += 1
            x = nums.at(i)
            lo, hi = i + 1, n
            while lo < hi:
                mid = (lo + hi) // 2
                if nums.at(mid) != x:
                    hi = mid
                else:
                    lo = mid + 1
            i = lo
        return ans

    def countBlocks_dnc(self, nums: Optional["BigArray"]) -> int:
        """
        Interview explanation:
        Alternate: divide-and-conquer on [l,r]; identical ends => one block.

        Algorithm:
        - Recurse mid; merge and subtract 1 if mid joins mid+1.

        Complexity: O(log n) queries when few blocks; O(m log n) worst.
        """

        def f(l: int, r: int) -> int:
            if nums.at(l) == nums.at(r):
                return 1
            mid = (l + r) // 2
            return f(l, mid) + f(mid + 1, r) - (1 if nums.at(mid) == nums.at(mid + 1) else 0)

        return f(0, nums.size() - 1)
# @lc code=end

