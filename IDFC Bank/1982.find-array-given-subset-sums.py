#
# @lc app=leetcode id=1982 lang=python3
#
# [1982] Find Array Given Subset Sums
#
# https://leetcode.com/problems/find-array-given-subset-sums/description/
#
# algorithms
# Hard (49.56%)
# Likes:    647
# Dislikes: 44
# Total Accepted:    8.4K
# Total Submissions: 17.0K
# Testcase Example:  "3"
#
# You are given an integer n representing the length of an unknown array that
# you are trying to recover. You are also given an array sums containing the
# values of all 2^n subset sums of the unknown array (in no particular order).
#
# Return the array ans of length n representing the unknown array. If multiple
# answers exist, return any of them.
#
# An array sub is a subset of an array arr if sub can be obtained from arr by
# deleting some (possibly zero or all) elements of arr. The sum of the elements
# in sub is one possible subset sum of arr. The sum of an empty array is
# considered to be 0.
#
# Note: Test cases are generated such that there will always be at least one
# correct answer.
#
# Example 1:
#
# Input: n = 3, sums = [-3,-2,-1,0,0,1,2,3]
# Output: [1,2,-3]
# Explanation: [1,2,-3] is able to achieve the given subset sums:
# - []: sum is 0
# - [1]: sum is 1
# - [2]: sum is 2
# - [1,2]: sum is 3
# - [-3]: sum is -3
# - [1,-3]: sum is -2
# - [2,-3]: sum is -1
# - [1,2,-3]: sum is 0
# Note that any permutation of [1,2,-3] and also any permutation of [-1,-2,3]
# will also be accepted.
#
# Example 2:
#
# Input: n = 2, sums = [0,0,0,0]
# Output: [0,0]
# Explanation: The only correct answer is [0,0].
#
# Example 3:
#
# Input: n = 4, sums = [0,0,5,5,4,-1,4,9,9,-1,4,3,4,8,3,8]
# Output: [0,-1,4,5]
# Explanation: [0,-1,4,5] is able to achieve the given subset sums.
#
# Constraints:
#
# 1 <= n <= 15
#
# sums.length == 2^n
#
# -10^4 <= sums[i] <= 10^4
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def recoverArray(self, n: int, sums: List[int]) -> List[int]:
        """
        Interview explanation:
        Given all 2^n subset sums, recover the n elements. Sort; candidate
        d = second - smallest; bipartition into S and S+d; keep the part that
        still contains 0 and record ±d.

        Algorithm:
        - Repeat n times: sort; d=sums[1]-sums[0]; Counter-split low group;
          if 0 in low: append d, sums=low; else append -d, sums=[x+d for x in low].

        Complexity: O(n * 2^n log 2^n) time, O(2^n) space.
        """
        cur = list(sums)
        ans: List[int] = []
        for _ in range(n):
            cur.sort()
            d = cur[1] - cur[0]
            count = Counter(cur)
            low: List[int] = []
            for x in cur:
                if count[x] == 0:
                    continue
                count[x] -= 1
                low.append(x)
                count[x + d] -= 1
            if 0 in low:
                ans.append(d)
                cur = low
            else:
                ans.append(-d)
                cur = [x + d for x in low]
        return ans

    def recoverArray_helper(self, n: int, sums: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate same reconstruction with an explicit split helper.

        Algorithm:
        - split(arr,d) -> low; choose sign so 0 remains in the active multiset.

        Complexity: O(n * 2^n log 2^n) time, O(2^n) space.
        """
        def split(arr: List[int], d: int) -> List[int]:
            count = Counter(arr)
            low = []
            for x in arr:
                if count[x] == 0:
                    continue
                count[x] -= 1
                low.append(x)
                count[x + d] -= 1
            return low

        cur = list(sums)
        ans = []
        for _ in range(n):
            cur.sort()
            d = cur[1] - cur[0]
            low = split(cur, d)
            if 0 in low:
                ans.append(d)
                cur = low
            else:
                ans.append(-d)
                cur = [x + d for x in low]
        return ans
# @lc code=end


