#
# @lc app=leetcode id=2195 lang=python3
#
# [2195] Append K Integers With Minimal Sum
#
# https://leetcode.com/problems/append-k-integers-with-minimal-sum/description/
#
# algorithms
# Medium (27.21%)
# Likes:    853
# Dislikes: 314
# Total Accepted:    43.8K
# Total Submissions: 160.8K
# Testcase Example:  "[1,4,25,10,25]\n2"
#
# You are given an integer array nums and an integer k. Append k unique positive
# integers that do not appear in nums to nums such that the resulting total sum
# is minimum.
#
# Return the sum of the k integers appended to nums.
#
#
#
# Example 1:
#
# Input: nums = [1,4,25,10,25], k = 2
# Output: 5
# Explanation: The two unique positive integers that do not appear in nums which
# we append are 2 and 3.
# The resulting sum of nums is 1 + 4 + 25 + 10 + 25 + 2 + 3 = 70, which is the
# minimum.
# The sum of the two integers appended is 2 + 3 = 5, so we return 5.
#
# Example 2:
#
# Input: nums = [5,6], k = 6
# Output: 25
# Explanation: The six unique positive integers that do not appear in nums which
# we append are 1, 2, 3, 4, 7, and 8.
# The resulting sum of nums is 5 + 6 + 1 + 2 + 3 + 4 + 7 + 8 = 36, which is the
# minimum.
# The sum of the six integers appended is 1 + 2 + 3 + 4 + 7 + 8 = 25, so we
# return 25.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#
#
# 1 <= k <= 10^8
#

# @lc code=start
from typing import List


class Solution:
    def minimalKSum(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Append k positive integers not in nums to minimize their sum. Take the
        smallest positives missing from nums.

        Algorithm:
        (sort unique)
        - Sort unique nums; walk gaps before/between/after; take from 1 upward
          skipping present; sum = arithmetic series.

        Complexity: O(n log n) time, O(n) space.
        """
        uniq = sorted(set(nums))
        ans = 0
        prev = 0
        for x in uniq:
            if k == 0:
                break
            # numbers prev+1 .. x-1 available
            if x > prev + 1:
                take = min(k, x - prev - 1)
                # sum of (prev+1) .. (prev+take)
                first = prev + 1
                last = prev + take
                ans += (first + last) * take // 2
                k -= take
            prev = x
        if k:
            first = prev + 1
            last = prev + k
            ans += (first + last) * k // 2
        return ans
# @lc code=end
