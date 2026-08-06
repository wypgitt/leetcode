#
# @lc app=leetcode id=493 lang=python3
#
# [493] Reverse Pairs
#
# https://leetcode.com/problems/reverse-pairs/description/
#
# algorithms
# Hard (34.9%)
# Likes:    7132
# Dislikes: 304
# Total Accepted:    399K
# Total Submissions: 1.1M
# Testcase Example:  "[1,3,2,3,1]"
#
# Given an integer array nums, return the number of reverse pairs in the array.
#
# A reverse pair is a pair (i, j) where:
#
# 0 <= i < j < nums.length and
#
# nums[i] > 2 * nums[j].
#
# Example 1:
#
# Input: nums = [1,3,2,3,1]
# Output: 2
# Explanation: The reverse pairs are:
# (1, 4) --> nums[1] = 3, nums[4] = 1, 3 > 2 * 1
# (3, 4) --> nums[3] = 3, nums[4] = 1, 3 > 2 * 1
#
# Example 2:
#
# Input: nums = [2,4,3,5,1]
# Output: 3
# Explanation: The reverse pairs are:
# (1, 4) --> nums[1] = 4, nums[4] = 1, 4 > 2 * 1
# (2, 4) --> nums[2] = 3, nums[4] = 1, 3 > 2 * 1
# (3, 4) --> nums[3] = 5, nums[4] = 1, 5 > 2 * 1
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# -2^31 <= nums[i] <= 2^31 - 1
#

# @lc code=start
from typing import List


class Solution:
    def reversePairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count pairs i < j with nums[i] > 2*nums[j] via modified merge sort:
        while merging, for each left element count how many right elements
        satisfy the inequality (two pointers on sorted halves).

        Algorithm:
        - Merge-sort nums; during merge of [lo..mid] and [mid+1..hi]:
          for each i in left, advance j while nums[i] > 2*nums[j]; add j-(mid+1).
        - Then merge as usual.

        Complexity: O(n log n) time, O(n) space.
        """
        def sort_count(lo: int, hi: int) -> int:
            if hi - lo <= 1:
                return 0
            mid = (lo + hi) // 2
            cnt = sort_count(lo, mid) + sort_count(mid, hi)
            j = mid
            for i in range(lo, mid):
                while j < hi and nums[i] > 2 * nums[j]:
                    j += 1
                cnt += j - mid
            # merge sorted halves
            merged = []
            i, j = lo, mid
            while i < mid and j < hi:
                if nums[i] <= nums[j]:
                    merged.append(nums[i])
                    i += 1
                else:
                    merged.append(nums[j])
                    j += 1
            merged.extend(nums[i:mid])
            merged.extend(nums[j:hi])
            nums[lo:hi] = merged
            return cnt

        return sort_count(0, len(nums))
# @lc code=end
