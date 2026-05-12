#
# @lc app=leetcode id=1296 lang=python3
#
# [1296] Divide Array in Sets of K Consecutive Numbers
#
# https://leetcode.com/problems/divide-array-in-sets-of-k-consecutive-numbers/description/
#
# algorithms
# Medium (59.22%)
# Likes:    1994
# Dislikes: 118
# Total Accepted:    129.1K
# Total Submissions: 217.9K
# Testcase Example:  '[1,2,3,3,4,4,5,6]\n4'
#
# Given an array of integers nums and a positive integer k, check whether it is
# possible to divide this array into sets of k consecutive numbers.
# 
# Return true if it is possible. Otherwise, return false.
# 
# 
# Example 1:
# 
# 
# Input: nums = [1,2,3,3,4,4,5,6], k = 4
# Output: true
# Explanation: Array can be divided into [1,2,3,4] and [3,4,5,6].
# 
# 
# Example 2:
# 
# 
# Input: nums = [3,2,1,2,3,4,3,4,5,9,10,11], k = 3
# Output: true
# Explanation: Array can be divided into [1,2,3] , [2,3,4] , [3,4,5] and
# [9,10,11].
# 
# 
# Example 3:
# 
# 
# Input: nums = [1,2,3,4], k = 3
# Output: false
# Explanation: Each array should be divided in subarrays of size 3.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= k <= nums.length <= 10^5
# 1 <= nums[i] <= 10^9
# 
# 
# 
# Note: This question is the same as 846:
# https://leetcode.com/problems/hand-of-straights/
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def isPossibleDivide(self, nums: List[int], k: int) -> bool:
        if len(nums) % k != 0:
            return False

        counts = Counter(nums)

        for start in sorted(counts):
            amount = counts[start]
            if amount == 0:
                continue

            for value in range(start, start + k):
                if counts[value] < amount:
                    return False
                counts[value] -= amount

        return True
# @lc code=end

# Explanation
# -----------
# Count each number. Process starts in sorted order; if count[start] is c, then
# those c copies must begin c groups at start because no smaller number remains
# to use them. Therefore every value start through start + k - 1 must have at
# least c copies, and we subtract c from each.
#
# Counter is the right data structure for multiplicities, and sorted keys give
# the greedy order that makes the forced-start argument valid.
#
# Edge cases: length not divisible by k; missing middle value in a needed
# consecutive run; duplicate-heavy inputs.
#
# Time complexity: O(n log n + n * k in the direct loop; with constraints this
# is accepted, and each subtraction is tied to a required group span).
# Space complexity: O(n) for counts.
