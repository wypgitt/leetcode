#
# @lc app=leetcode id=3936 lang=python3
#
# [3936] Minimum Swaps to Move Zeros to End
#
# https://leetcode.com/problems/minimum-swaps-to-move-zeros-to-end/description/
#
# algorithms
# Easy (60.65%)
# Likes:    32
# Dislikes: 1
# Total Accepted:    39.3K
# Total Submissions: 64.8K
# Testcase Example:  "[0,1,0,3,12]"
#
#
# You are given an integer array nums.
#
# In one operation, you can choose any two distinct indices i and j and
# swap nums[i] and nums[j].
#
# Return an integer denoting the minimum number of operations required to
# move all 0s to the end of the array.
#
# Example 1:
#
# Input: nums = [0,1,0,3,12]
#
# Output: 2
#
# Explanation:
#
# We perform the following swap operations:
#
# Swap nums[0] and nums[3], giving nums = [3, 1, 0, 0, 12].
#
# Swap nums[2] and nums[4], giving nums = [3, 1, 12, 0, 0].
#
# Thus, the answer is 2.
#
# Example 2:
#
# Input: nums = [0,1,0,2]
#
# Output: 1
#
# Explanation:
#
# We perform the following swap operations:
#
# Swap nums[0] and nums[3], giving nums = [2, 1, 0, 0].
#
# Thus, the answer is 1.
#
# Example 3:
#
# Input: nums = [1,2,0]
#
# Output: 0
#
# Explanation:
#
# The array already satisfies the condition. Therefore, no swap operations
# are needed.
#
# Constraints:
#
# 1 <= nums.length <= 100
#
# 0 <= nums[i] <= 100
#

# @lc code=start

class Solution:
    def minimumSwaps(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Any pair can be swapped, so zeros can move freely to the suffix of length
        z (#zeros). Min swaps equals how many non-zeros currently sit in that
        suffix (each needs one swap with a zero from the prefix).

        Algorithm:
        - z = count of zeros; count non-zeros among the last z positions.

        Complexity: O(n) time, O(1) space.
        """
        z = sum(1 for x in nums if x == 0)
        return sum(1 for x in nums[-z:] if x != 0) if z else 0

    def minimumSwaps_prefix(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Alternate: count zeros among the first n-z positions (same quantity).

        Algorithm:
        - Return number of zeros in nums[:n-z].

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        z = sum(x == 0 for x in nums)
        return sum(x == 0 for x in nums[: n - z])
# @lc code=end
