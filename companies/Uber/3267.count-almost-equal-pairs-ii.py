#
# @lc app=leetcode id=3267 lang=python3
#
# [3267] Count Almost Equal Pairs II
#
# https://leetcode.com/problems/count-almost-equal-pairs-ii/description/
#
# algorithms
# Hard (27.25%)
# Likes:    81
# Dislikes: 24
# Total Accepted:    9.6K
# Total Submissions: 35.2K
# Testcase Example:  "[1023,2310,2130,213]"
#
#
# Attention: In this version, the number of operations that can be
# performed, has been increased to twice.
#
# You are given an array nums consisting of positive integers.
#
# We call two integers x and y almost equal if both integers can become
# equal after performing the following operation at most twice:
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
# Input: nums = [1023,2310,2130,213]
#
# Output: 4
#
# Explanation:
#
# The almost equal pairs of elements are:
#
# 1023 and 2310. By swapping the digits 1 and 2, and then the digits 0 and
# 3 in 1023, you get 2310.
#
# 1023 and 213. By swapping the digits 1 and 0, and then the digits 1 and
# 2 in 1023, you get 0213, which is 213.
#
# 2310 and 213. By swapping the digits 2 and 0, and then the digits 3 and
# 2 in 2310, you get 0213, which is 213.
#
# 2310 and 2130. By swapping the digits 3 and 1 in 2310, you get 2130.
#
# Example 2:
#
# Input: nums = [1,10,100]
#
# Output: 3
#
# Explanation:
#
# The almost equal pairs of elements are:
#
# 1 and 10. By swapping the digits 1 and 0 in 10, you get 01 which is 1.
#
# 1 and 100. By swapping the second 0 with the digit 1 in 100, you get
# 001, which is 1.
#
# 10 and 100. By swapping the first 0 with the digit 1 in 100, you get
# 010, which is 10.
#
# Constraints:
#
# 2 <= nums.length <= 5000
#
# 1 <= nums[i] < 10^7
#

# @lc code=start

from typing import List
from collections import Counter


class Solution:
    def countPairs(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Like I, but at most two digit swaps total on one number (enough to cover
        split 1+1 ops). Pad all values to the same digit width; count via
        2-swap neighborhoods against prior frequencies.

        Algorithm:
        - For each num, generate all values reachable with ≤2 swaps on the padded
          digit string; ans += sum of freq[v] over that set; then freq[num]++.

        Complexity: O(n * D^4) time, O(n + D^4) space (D ≤ 7).
        """
        max_len = max(len(str(x)) for x in nums)
        freq: Counter = Counter()
        ans = 0

        def variants(x: int) -> set[int]:
            s = list(str(x).zfill(max_len))
            m = len(s)
            res = {int(''.join(s))}
            # 1 swap
            for i in range(m):
                for j in range(i + 1, m):
                    s[i], s[j] = s[j], s[i]
                    res.add(int(''.join(s)))
                    # 2nd swap
                    for a in range(m):
                        for b in range(a + 1, m):
                            s[a], s[b] = s[b], s[a]
                            res.add(int(''.join(s)))
                            s[a], s[b] = s[b], s[a]
                    s[i], s[j] = s[j], s[i]
            return res

        for num in nums:
            for v in variants(num):
                ans += freq[v]
            freq[num] += 1
        return ans
# @lc code=end
