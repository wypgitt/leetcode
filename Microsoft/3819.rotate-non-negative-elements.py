#
# @lc app=leetcode id=3819 lang=python3
#
# [3819] Rotate Non Negative Elements
#
# https://leetcode.com/problems/rotate-non-negative-elements/description/
#
# algorithms
# Medium (48.12%)
# Likes:    80
# Dislikes: 10
# Total Accepted:    44.5K
# Total Submissions: 92.4K
# Testcase Example:  "[1,-2,3,-4]\n3"
#
#
# You are given an integer array nums and an integer k.
#
# Rotate only the non-negative elements of the array to the left by k
# positions, in a cyclic manner.
#
# All negative elements must stay in their original positions and must not
# move.
#
# After rotation, place the non-negative elements back into the array in
# the new order, filling only the positions that originally contained
# non-negative values and skipping all negative positions.
#
# Return the resulting array.
#
# Example 1:
#
# Input: nums = [1,-2,3,-4], k = 3
#
# Output: [3,-2,1,-4]
#
# Explanation:​​​​​​​
#
# The non-negative elements, in order, are [1, 3].
#
# Left rotation with k = 3 results in:
#
# [1, 3] -> [3, 1] -> [1, 3] -> [3, 1]
#
# Placing them back into the non-negative indices results in [3, -2, 1,
# -4].
#
# Example 2:
#
# Input: nums = [-3,-2,7], k = 1
#
# Output: [-3,-2,7]
#
# Explanation:
#
# The non-negative elements, in order, are [7].
#
# Left rotation with k = 1 results in [7].
#
# Placing them back into the non-negative indices results in [-3, -2, 7].
#
# Example 3:
#
# Input: nums = [5,4,-9,6], k = 2
#
# Output: [6,5,-9,4]
#
# Explanation:
#
# The non-negative elements, in order, are [5, 4, 6].
#
# Left rotation with k = 2 results in [6, 5, 4].
#
# Placing them back into the non-negative indices results in [6, 5, -9,
# 4].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^5 <= nums[i] <= 10^5
#
# 0 <= k <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def rotateElements(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Left-rotate only non-negative values by k (cyclic); negatives stay
        fixed in place. Put rotated values back into non-negative slots.

        Algorithm:
        - Collect non-negatives; if empty return nums.
        - Rotate: vals = vals[k%len:] + vals[:k%len].
        - Write back into indices where nums[i] >= 0.

        Complexity: O(n) time, O(n) space.
        """
        vals = [x for x in nums if x >= 0]
        if not vals:
            return nums
        m = len(vals)
        k %= m
        vals = vals[k:] + vals[:k]
        ans = nums[:]
        j = 0
        for i in range(len(ans)):
            if ans[i] >= 0:
                ans[i] = vals[j]
                j += 1
        return ans
# @lc code=end
