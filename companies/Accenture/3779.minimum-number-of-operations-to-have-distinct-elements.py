#
# @lc app=leetcode id=3779 lang=python3
#
# [3779] Minimum Number of Operations to Have Distinct Elements
#
# https://leetcode.com/problems/minimum-number-of-operations-to-have-distinct-elements/description/
#
# algorithms
# Medium (42.60%)
# Likes:    49
# Dislikes: 2
# Total Accepted:    29.2K
# Total Submissions: 68.5K
# Testcase Example:  "[3,8,3,6,5,8]"
#
#
# You are given an integer array nums.
#
# In one operation, you remove the first three elements of the current
# array. If there are fewer than three elements remaining, all remaining
# elements are removed.
#
# Repeat this operation until the array is empty or contains no duplicate
# values.
#
# Return an integer denoting the number of operations required.
#
# Example 1:
#
# Input: nums = [3,8,3,6,5,8]
#
# Output: 1
#
# Explanation:
#
# In the first operation, we remove the first three elements. The
# remaining elements [6, 5, 8] are all distinct, so we stop. Only one
# operation is needed.
#
# Example 2:
#
# Input: nums = [2,2]
#
# Output: 1
#
# Explanation:
#
# After one operation, the array becomes empty, which meets the stopping
# condition.
#
# Example 3:
#
# Input: nums = [4,3,5,1,2]
#
# Output: 0
#
# Explanation:
#
# All elements in the array are distinct, therefore no operations are
# needed.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Operations always delete a prefix of length 3 (or the remainder). The
        surviving suffix must be the longest duplicate-free suffix; ops = ceil of
        deleted prefix length / 3.

        Algorithm:
        - Scan from the right, collecting values until a duplicate appears.
        - Return ceil(remaining_prefix_len / 3).

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        i = len(nums) - 1
        while i >= 0:
            if nums[i] in seen:
                break
            seen.add(nums[i])
            i -= 1
        # prefix nums[0..i] must be removed
        return (i + 3) // 3  # ceil((i+1)/3); i=-1 -> 0

    def minOperations_sim(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: simulate removals until the array is empty or unique.

        Algorithm:
        - While len>=1 and has dup: drop first 3; count++.

        Complexity: O(n^2) worst via repeated uniqueness checks, O(n) space.
        """
        a = nums[:]
        ops = 0
        while a and len(a) != len(set(a)):
            a = a[3:]
            ops += 1
        return ops
# @lc code=end
