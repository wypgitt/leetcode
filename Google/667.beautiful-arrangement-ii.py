#
# @lc app=leetcode id=667 lang=python3
#
# [667] Beautiful Arrangement II
#
# https://leetcode.com/problems/beautiful-arrangement-ii/description/
#
# algorithms
# Medium (61.3%)
# Likes:    832
# Dislikes: 1062
# Total Accepted:    63.1K
# Total Submissions: 103K
# Testcase Example:  "3"
#
# Given two integers n and k, construct a list answer that contains n different
# positive integers ranging from 1 to n and obeys the following requirement:
#
# Suppose this list is answer = [a_1, a_2, a_3, ... , a_n], then the list [|a_1
# - a_2|, |a_2 - a_3|, |a_3 - a_4|, ... , |a_n-1 - a_n|] has exactly k distinct
# integers.
#
# Return the list answer. If there multiple valid answers, return any of them.
#
# Example 1:
#
# Input: n = 3, k = 1
# Output: [1,2,3]
# Explanation: The [1,2,3] has three different positive integers ranging from 1
# to 3, and the [1,1] has exactly 1 distinct integer: 1
#
# Example 2:
#
# Input: n = 3, k = 2
# Output: [1,3,2]
# Explanation: The [1,3,2] has three different positive integers ranging from 1
# to 3, and the [2,1] has exactly 2 distinct integers: 1 and 2.
#
# Constraints:
#
# 1 <= k < n <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def constructArray(self, n: int, k: int) -> List[int]:
        """
        Interview explanation:
        Build a permutation of 1..n with exactly k distinct adjacent absolute
        differences. Place 1..(n-k) ascending (diff 1), then zigzag the remaining
        numbers to create diffs k, k-1, ..., 1.

        Algorithm:
        - Append 1..n-k-1? Actually: range(1, n-k) then zigzag [n-k .. n]
          as lo, hi, lo+1, hi-1, ...

        Complexity: O(n) time and space.
        """
        res = list(range(1, n - k))
        lo, hi = n - k, n
        while lo <= hi:
            res.append(lo)
            lo += 1
            if lo <= hi:
                res.append(hi)
                hi -= 1
        return res
# @lc code=end
