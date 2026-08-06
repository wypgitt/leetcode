#
# @lc app=leetcode id=1105 lang=python3
#
# [1105] Filling Bookcase Shelves
#
# https://leetcode.com/problems/filling-bookcase-shelves/description/
#
# algorithms
# Medium (68.64%)
# Likes:    2701
# Dislikes: 270
# Total Accepted:    162K
# Total Submissions: 236K
# Testcase Example:  "[[1,1],[2,3],[2,3],[1,1],[1,1],[1,1],[1,2]]"
#
# You are given an array books where books[i] = [thickness_i, height_i]
# indicates the thickness and height of the i^th book. You are also given an
# integer shelfWidth.
#
# We want to place these books in order onto bookcase shelves that have a total
# width shelfWidth.
#
# We choose some of the books to place on this shelf such that the sum of their
# thickness is less than or equal to shelfWidth, then build another level of
# the shelf of the bookcase so that the total height of the bookcase has
# increased by the maximum height of the books we just put down. We repeat this
# process until there are no more books to place.
#
# Note that at each step of the above process, the order of the books we place
# is the same order as the given sequence of books.
#
# For example, if we have an ordered list of 5 books, we might place the first
# and second book onto the first shelf, the third book on the second shelf, and
# the fourth and fifth book on the last shelf.
#
# Return the minimum possible height that the total bookshelf can be after
# placing shelves in this manner.
#
# Example 1:
#
# Input: books = [[1,1],[2,3],[2,3],[1,1],[1,1],[1,1],[1,2]], shelfWidth = 4
# Output: 6
# Explanation:
# The sum of the heights of the 3 shelves is 1 + 3 + 2 = 6.
# Notice that book number 2 does not have to be on the first shelf.
#
# Example 2:
#
# Input: books = [[1,3],[2,4],[3,2]], shelfWidth = 6
# Output: 4
#
# Constraints:
#
# 1 <= books.length <= 1000
#
# 1 <= thickness_i <= shelfWidth <= 1000
#
# 1 <= height_i <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def minHeightShelves(self, books: List[List[int]], shelfWidth: int) -> int:
        """
        Interview explanation:
        Place books in order; DP where dp[i] = min height to place first i books.
        For each i, try putting books j..i-1 on the last shelf (fitting width),
        height = max heights on that shelf; dp[i]=min(dp[j]+shelf_h).

        Algorithm (DP):
        - dp[0]=0; dp[i]=∞.
        - For i in 1..n: width=0,h=0; for j from i-1 down to 0: add books[j];
          if width>shelfWidth break; h=max(h,height); dp[i]=min(dp[i],dp[j]+h).

        Complexity: O(n²) time, O(n) space.
        """
        n = len(books)
        dp = [0] + [10**9] * n
        for i in range(1, n + 1):
            width = 0
            height = 0
            for j in range(i - 1, -1, -1):
                width += books[j][0]
                if width > shelfWidth:
                    break
                height = max(height, books[j][1])
                dp[i] = min(dp[i], dp[j] + height)
        return dp[n]
# @lc code=end
