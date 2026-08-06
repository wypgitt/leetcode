#
# @lc app=leetcode id=1695 lang=python3
#
# [1695] Maximum Erasure Value
#
# https://leetcode.com/problems/maximum-erasure-value/description/
#
# algorithms
# Medium (64.4%)
# Likes:    3425
# Dislikes: 68
# Total Accepted:    306K
# Total Submissions: 475K
# Testcase Example:  "[4,2,4,5,6]"
#
# You are given an array of positive integers nums and want to erase a subarray
# containing unique elements. The score you get by erasing the subarray is
# equal to the sum of its elements.
#
# Return the maximum score you can get by erasing exactly one subarray.
#
# An array b is called to be a subarray of a if it forms a contiguous
# subsequence of a, that is, if it is equal to a[l],a[l+1],...,a[r] for some
# (l,r).
#
# Example 1:
#
# Input: nums = [4,2,4,5,6]
# Output: 17
# Explanation: The optimal subarray here is [2,4,5,6].
#
# Example 2:
#
# Input: nums = [5,2,1,2,5,2,1,2,5]
# Output: 8
# Explanation: The optimal subarray here is [5,2,1] or [1,2,5].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maximumUniqueSubarray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Max sum of a subarray with all unique elements (erase score). Sliding
        window + set/last-index; expand right, shrink left on duplicates.

        Algorithm (sliding window):
        - left=0, cur=0, seen=set; for right: while nums[right] in seen: remove left;
          add; track max cur.

        Complexity: O(n) time, O(n) space.
        """
        seen = set()
        left = cur = ans = 0
        for right, v in enumerate(nums):
            while v in seen:
                seen.remove(nums[left])
                cur -= nums[left]
                left += 1
            seen.add(v)
            cur += v
            ans = max(ans, cur)
        return ans
# @lc code=end
