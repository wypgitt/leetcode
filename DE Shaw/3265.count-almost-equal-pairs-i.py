#
# @lc app=leetcode id=3265 lang=python3
#
# [3265] Count Almost Equal Pairs I
#
# https://leetcode.com/problems/count-almost-equal-pairs-i/description/
#
# algorithms
# Medium (38.57%)
# Likes:    161
# Dislikes: 26
# Total Accepted:    29.9K
# Total Submissions: 77.5K
# Testcase Example:  "[3,12,30,17,21]"
#
#
# You are given an array nums consisting of positive integers.
#
# We call two integers x and y in this problem almost equal if both
# integers can become equal after performing the following operation at
# most once:
#
# Choose either x or y and swap any two digits within the chosen number.
#
# Return the number of indices i and j in nums where i < j such that
# nums[i] and nums[j] are almost equal.
#
# Note that it is allowed for an integer to have leading zeros after
# performing an operation.
#
# Example 1:
#
# Input: nums = [3,12,30,17,21]
#
# Output: 2
#
# Explanation:
#
# The almost equal pairs of elements are:
#
# 3 and 30. By swapping 3 and 0 in 30, you get 3.
#
# 12 and 21. By swapping 1 and 2 in 12, you get 21.
#
# Example 2:
#
# Input: nums = [1,1,1,1,1]
#
# Output: 10
#
# Explanation:
#
# Every two elements in the array are almost equal.
#
# Example 3:
#
# Input: nums = [123,231]
#
# Output: 0
#
# Explanation:
#
# We cannot swap any two digits of 123 or 231 to reach the other.
#
# Constraints:
#
# 2 <= nums.length <= 100
#
# 1 <= nums[i] <= 10^6
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def countPairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        x,y are almost equal if one can become the other with at most one digit
        swap (leading zeros allowed). Count pairs via swap-neighborhood lookups.

        Algorithm:
        - Process left to right; for each num generate itself and all 1-swap forms
          (pad to max digit length). Add freq of those strings/ints seen as originals.
        - Then freq[num] += 1.

        Complexity: O(n * D^2) time, O(n) space (D ≤ 7).
        """
        max_len = max(len(str(x)) for x in nums)
        freq: Counter = Counter()
        ans = 0

        def variants(x: int) -> set[int]:
            s = list(str(x).zfill(max_len))
            res = {int(''.join(s))}
            m = len(s)
            for i in range(m):
                for j in range(i + 1, m):
                    s[i], s[j] = s[j], s[i]
                    res.add(int(''.join(s)))
                    s[i], s[j] = s[j], s[i]
            return res

        for num in nums:
            for v in variants(num):
                ans += freq[v]
            freq[num] += 1
        return ans
# @lc code=end
