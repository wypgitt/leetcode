#
# @lc app=leetcode id=3191 lang=python3
#
# [3191] Minimum Operations to Make Binary Array Elements Equal to One I
#
# https://leetcode.com/problems/minimum-operations-to-make-binary-array-elements-equal-to-one-i/description/
#
# algorithms
# Medium (80.44%)
# Likes:    693
# Dislikes: 36
# Total Accepted:    215.4K
# Total Submissions: 267.7K
# Testcase Example:  "[0,1,1,1,0,0]"
#
#
# You are given a binary array nums.
#
# You can do the following operation on the array any number of times
# (possibly zero):
#
# Choose any 3 consecutive elements from the array and flip all of them.
#
# Flipping an element means changing its value from 0 to 1, and from 1 to
# 0.
#
# Return the minimum number of operations required to make all elements in
# nums equal to 1. If it is impossible, return -1.
#
# Example 1:
#
# Input: nums = [0,1,1,1,0,0]
#
# Output: 3
#
# Explanation:
#
# We can do the following operations:
#
# Choose the elements at indices 0, 1 and 2. The resulting array is nums =
# [1,0,0,1,0,0].
#
# Choose the elements at indices 1, 2 and 3. The resulting array is nums =
# [1,1,1,0,0,0].
#
# Choose the elements at indices 3, 4 and 5. The resulting array is nums =
# [1,1,1,1,1,1].
#
# Example 2:
#
# Input: nums = [0,1,1,1]
#
# Output: -1
#
# Explanation:
#
# It is impossible to make all elements equal to 1.
#
# Constraints:
#
# 3 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 1
#

# @lc code=start

from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Flip any 3 consecutive bits. Must make the array all 1s. Greedy: when
        position i is 0, flip i..i+2 (only way to fix i without touching earlier).

        Algorithm:
        - Scan left to right; if nums[i]==0 and i+2 < n, flip three bits and ++ops.
        - If any trailing 0 remains, return -1.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(nums)
        ops = 0
        for i in range(n - 2):
            if nums[i] == 0:
                nums[i] ^= 1
                nums[i + 1] ^= 1
                nums[i + 2] ^= 1
                ops += 1
        return ops if nums[-1] == 1 and nums[-2] == 1 else -1

    def minOperations_copy(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same greedy without mutating the caller's list (work on a copy).

        Algorithm:
        - Copy then apply the left-to-right forced flips.

        Complexity: O(n) time, O(n) space.
        """
        a = nums[:]
        return self.minOperations(a)
# @lc code=end
