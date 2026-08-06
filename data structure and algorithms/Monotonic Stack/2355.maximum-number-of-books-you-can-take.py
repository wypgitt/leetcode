#
# @lc app=leetcode id=2355 lang=python3
#
# [2355] Maximum Number of Books You Can Take
#
# https://leetcode.com/problems/maximum-number-of-books-you-can-take/description/
#
# algorithms
# Hard (39.48%)
# Likes:    298
# Dislikes: 41
# Total Accepted:    13.5K
# Total Submissions: 34.3K
# Testcase Example:  "[8,5,2,7,9]"
#
#
# You are given a 0-indexed integer array books of length n where books[i]
# denotes the number of books on the i^th shelf of a bookshelf.
#
# You are going to take books from a contiguous section of the bookshelf
# spanning from l to r where 0 <= l <= r < n. For each index i in the
# range l <= i < r, you must take strictly fewer books from shelf i than
# shelf i + 1.
#
# Return the maximum number of books you can take from the bookshelf.
#
# Example 1:
#
# Input: books = [8,5,2,7,9]
# Output: 19
# Explanation:
# - Take 1 book from shelf 1.
# - Take 2 books from shelf 2.
# - Take 7 books from shelf 3.
# - Take 9 books from shelf 4.
# You have taken 19 books, so return 19.
# It can be proven that 19 is the maximum number of books you can take.
#
# Example 2:
#
# Input: books = [7,0,3,4,5]
# Output: 12
# Explanation:
# - Take 3 books from shelf 2.
# - Take 4 books from shelf 3.
# - Take 5 books from shelf 4.
# You have taken 12 books so return 12.
# It can be proven that 12 is the maximum number of books you can take.
#
# Example 3:
#
# Input: books = [8,2,3,7,3,4,0,1,4,3]
# Output: 13
# Explanation:
# - Take 1 book from shelf 0.
# - Take 2 books from shelf 1.
# - Take 3 books from shelf 2.
# - Take 7 books from shelf 3.
# You have taken 13 books so return 13.
# It can be proven that 13 is the maximum number of books you can take.
#
# Constraints:
#
# 1 <= books.length <= 10^5
#
# 0 <= books[i] <= 10^5
#
# @lc code=start

from typing import List


class Solution:
    def maximumBooks(self, books: List[int]) -> int:
        """
        Interview explanation:
        Premium: Take books from a contiguous shelf range ending at some i,
        taking a non-decreasing-by-1 sequence ending with books[i] books from
        shelf i (at most books[j] from j). Maximize total books taken.

        Algorithm:
        - Monotonic stack + DP: dp[i] = max books ending at i; stack finds
          previous index where books[j]-j < books[i]-i; arithmetic series sum.

        Complexity: O(n) time, O(n) space.
        """
        n = len(books)

        def calc(l: int, r: int) -> int:
            cnt = min(books[r], r - l + 1)
            return (2 * books[r] - (cnt - 1)) * cnt // 2

        stack: List[int] = []
        dp = [0] * n
        for i in range(n):
            while stack and books[stack[-1]] - stack[-1] >= books[i] - i:
                stack.pop()
            if not stack:
                dp[i] = calc(0, i)
            else:
                j = stack[-1]
                dp[i] = dp[j] + calc(j + 1, i)
            stack.append(i)
        return max(dp)
# @lc code=end
