#
# @lc app=leetcode id=2217 lang=python3
#
# [2217] Find Palindrome With Fixed Length
#
# https://leetcode.com/problems/find-palindrome-with-fixed-length/description/
#
# algorithms
# Medium (38.15%)
# Likes:    672
# Dislikes: 297
# Total Accepted:    28.6K
# Total Submissions: 74.9K
# Testcase Example:  "[1,2,3,4,5,90]\n3"
#
# Given an integer array queries and a positive integer intLength, return an
# array answer where answer[i] is either the queries[i]^th smallest positive
# palindrome of length intLength or -1 if no such palindrome exists.
#
# A palindrome is a number that reads the same backwards and forwards.
# Palindromes cannot have leading zeros.
#
#
#
# Example 1:
#
# Input: queries = [1,2,3,4,5,90], intLength = 3
# Output: [101,111,121,131,141,999]
# Explanation:
# The first few palindromes of length 3 are:
# 101, 111, 121, 131, 141, 151, 161, 171, 181, 191, 202, ...
# The 90^th palindrome of length 3 is 999.
#
# Example 2:
#
# Input: queries = [2,4,6], intLength = 4
# Output: [1111,1331,1551]
# Explanation:
# The first six palindromes of length 4 are:
# 1001, 1111, 1221, 1331, 1441, and 1551.
#
#
#
# Constraints:
#
#
# 1 <= queries.length <= 5 * 10^4
#
#
# 1 <= queries[i] <= 10^9
#
#
# 1 <= intLength <= 15
#

# @lc code=start
from typing import List


class Solution:
    def kthPalindrome(self, queries: List[int], intLength: int) -> List[int]:
        """
        Interview explanation:
        Among positive intLength-digit palindromes in ascending order, answer
        queries[i]-th one (1-indexed), or -1 if missing.

        Algorithm:
        - First half length = (intLength+1)//2; first half ranges from
          10^(half-1) to 10^half-1. Map query index to first half, mirror.

        Complexity: O(q * intLength) time, O(1) extra space.
        """
        half = (intLength + 1) // 2
        start = 10 ** (half - 1)
        count = 9 * 10 ** (half - 1)
        ans = []
        for q in queries:
            if q > count:
                ans.append(-1)
                continue
            first = str(start + q - 1)
            if intLength % 2 == 0:
                pal = first + first[::-1]
            else:
                pal = first + first[-2::-1]
            ans.append(int(pal))
        return ans
# @lc code=end
