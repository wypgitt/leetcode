#
# @lc app=leetcode id=3354 lang=python3
#
# [3354] Make Array Elements Equal to Zero
#
# https://leetcode.com/problems/make-array-elements-equal-to-zero/description/
#
# algorithms
# Easy (68.13%)
# Likes:    563
# Dislikes: 167
# Total Accepted:    137.4K
# Total Submissions: 201.6K
# Testcase Example:  "[1,0,2,0,3]"
#
#
# You are given an integer array nums.
#
# Start by selecting a starting position curr such that nums[curr] == 0,
# and choose a movement direction of either left or right.
#
# After that, you repeat the following process:
#
# If curr is out of the range [0, n - 1], this process ends.
#
# If nums[curr] == 0, move in the current direction by incrementing curr
# if you are moving right, or decrementing curr if you are moving left.
#
# Else if nums[curr] > 0:
#
# Decrement nums[curr] by 1.
#
# Reverse your movement direction (left becomes right and vice versa).
#
# Take a step in your new direction.
#
# A selection of the initial position curr and movement direction is
# considered valid if every element in nums becomes 0 by the end of the
# process.
#
# Return the number of possible valid selections.
#
# Example 1:
#
# Input: nums = [1,0,2,0,3]
#
# Output: 2
#
# Explanation:
#
# The only possible valid selections are the following:
#
# Choose curr = 3, and a movement direction to the left.
#
# [1,0,2,0,3] -> [1,0,2,0,3] -> [1,0,1,0,3] -> [1,0,1,0,3] -> [1,0,1,0,2]
# -> [1,0,1,0,2] -> [1,0,0,0,2] -> [1,0,0,0,2] -> [1,0,0,0,1] ->
# [1,0,0,0,1] -> [1,0,0,0,1] -> [1,0,0,0,1] -> [0,0,0,0,1] -> [0,0,0,0,1]
# -> [0,0,0,0,1] -> [0,0,0,0,1] -> [0,0,0,0,0].
#
# Choose curr = 3, and a movement direction to the right.
#
# [1,0,2,0,3] -> [1,0,2,0,3] -> [1,0,2,0,2] -> [1,0,2,0,2] -> [1,0,1,0,2]
# -> [1,0,1,0,2] -> [1,0,1,0,1] -> [1,0,1,0,1] -> [1,0,0,0,1] ->
# [1,0,0,0,1] -> [1,0,0,0,0] -> [1,0,0,0,0] -> [1,0,0,0,0] -> [1,0,0,0,0]
# -> [0,0,0,0,0].
#
# Example 2:
#
# Input: nums = [2,3,4,0,4,1,0]
#
# Output: 0
#
# Explanation:
#
# There are no possible valid selections.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 0 <= nums[i] <= 100
#
# There is at least one element i where nums[i] == 0.
#

# @lc code=start

from typing import List


class Solution:
    def countValidSelections(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Start on a 0 and walk, decrementing positives and bouncing. A start is
        valid iff the process zeros the array. With total sum S, at zero index i
        with left sum L and right R (=S-L): both dirs if L==R; one dir if |L-R|==1.

        Algorithm:
        - Prefix left sum; for each zero, compare left vs right.

        Complexity: O(n) time, O(1) space.
        """
        total = sum(nums)
        left = 0
        ans = 0
        for x in nums:
            if x == 0:
                right = total - left
                if left == right:
                    ans += 2
                elif abs(left - right) == 1:
                    ans += 1
            left += x
        return ans

    def countValidSelections_simulate(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: simulate every (start, direction) since n and values are small.

        Algorithm:
        - Copy array; walk with bounce/decrement until exit; check all zeros.

        Complexity: O(n * sum(nums)) time, O(n) space.
        """
        n = len(nums)
        ans = 0
        for i, v in enumerate(nums):
            if v != 0:
                continue
            for d in (-1, 1):
                a = nums[:]
                cur, step = i, d
                while 0 <= cur < n:
                    if a[cur] == 0:
                        cur += step
                    else:
                        a[cur] -= 1
                        step = -step
                        cur += step
                if all(x == 0 for x in a):
                    ans += 1
        return ans
# @lc code=end
