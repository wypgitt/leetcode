#
# @lc app=leetcode id=18 lang=python3
#
# [18] 4Sum
#
# https://leetcode.com/problems/4sum/description/
#
# algorithms
# Medium (40.56%)
# Likes:    12899
# Dislikes: 1540
# Total Accepted:    1.7M
# Total Submissions: 4.2M
# Testcase Example:  '[1,0,-1,0,-2,2]\n0'
#
# Given an array nums of n integers, return an array of all the unique
# quadruplets [nums[a], nums[b], nums[c], nums[d]] such that:
# 
# 
# 0 <= a, b, c, d < n
# a, b, c, and d are distinct.
# nums[a] + nums[b] + nums[c] + nums[d] == target
# 
# 
# You may return the answer in any order.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,0,-1,0,-2,2], target = 0
# Output: [[-2,-1,1,2],[-2,0,0,2],[-1,0,0,1]]
# 
# 
# Example 2:
# 
# 
# Input: nums = [2,2,2,2,2], target = 8
# Output: [[2,2,2,2]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 200
# -10^9 <= nums[i] <= 10^9
# -10^9 <= target <= 10^9
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def fourSum(self, nums: List[int], target: int) -> List[List[int]]:
        """
        Interview explanation:
        Sorting plus two fixed indices reduces 4Sum to the two-pointer 2Sum
        problem. Sorting is the key data organization: it gives monotonic
        pointer movement and makes duplicate skipping deterministic.

        Algorithm:
        - Sort nums.
        - Pick unique i and unique j after i.
        - Use left/right to find pairs completing target.
        - Skip duplicates after each emitted quadruplet.

        Edge cases and tests:
        - Length < 4 returns [].
        - Many duplicate values, e.g. [2,2,2,2,2], emit one quadruplet.
        - Large positive/negative values work because Python ints do not overflow.

        Complexity: O(n^3) time, O(1) extra space excluding output.
        """
        nums.sort()
        ans = []
        n = len(nums)

        for i in range(n - 3):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            for j in range(i + 1, n - 2):
                if j > i + 1 and nums[j] == nums[j - 1]:
                    continue
                left, right = j + 1, n - 1
                while left < right:
                    total = nums[i] + nums[j] + nums[left] + nums[right]
                    if total == target:
                        ans.append([nums[i], nums[j], nums[left], nums[right]])
                        left += 1
                        right -= 1
                        while left < right and nums[left] == nums[left - 1]:
                            left += 1
                        while left < right and nums[right] == nums[right + 1]:
                            right -= 1
                    elif total < target:
                        left += 1
                    else:
                        right -= 1

        return ans
# @lc code=end


