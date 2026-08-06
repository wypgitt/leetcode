#
# @lc app=leetcode id=3200 lang=python3
#
# [3200] Maximum Height of a Triangle
#
# https://leetcode.com/problems/maximum-height-of-a-triangle/description/
#
# algorithms
# Easy (44.70%)
# Likes:    168
# Dislikes: 32
# Total Accepted:    45.5K
# Total Submissions: 101.8K
# Testcase Example:  "2\n4"
#
#
# You are given two integers red and blue representing the count of red
# and blue colored balls. You have to arrange these balls to form a
# triangle such that the 1^st row will have 1 ball, the 2^nd row will have
# 2 balls, the 3^rd row will have 3 balls, and so on.
#
# All the balls in a particular row should be the same color, and adjacent
# rows should have different colors.
#
# Return the maximum height of the triangle that can be achieved.
#
# Example 1:
#
# Input: red = 2, blue = 4
#
# Output: 3
#
# Explanation:
#
# The only possible arrangement is shown above.
#
# Example 2:
#
# Input: red = 2, blue = 1
#
# Output: 2
#
# Explanation:
#
# The only possible arrangement is shown above.
#
# Example 3:
#
# Input: red = 1, blue = 1
#
# Output: 1
#
# Example 4:
#
# Input: red = 10, blue = 1
#
# Output: 2
#
# Explanation:
#
# The only possible arrangement is shown above.
#
# Constraints:
#
# 1 <= red, blue <= 100
#

# @lc code=start

class Solution:
    def maxHeightOfTriangle(self, red: int, blue: int) -> int:
        """
        Interview explanation:
        Build rows of size 1,2,3,... alternating colors; all balls in a row same
        color. Try both starting colors; take max achievable height.

        Algorithm:
        - Simulate: for start color, consume row k from alternating piles until short.

        Complexity: O(H) time with H ~ sqrt(red+blue), O(1) space.
        """
        def height(first: int, second: int) -> int:
            h = 0
            need = 1
            while True:
                if need & 1:
                    if first < need:
                        break
                    first -= need
                else:
                    if second < need:
                        break
                    second -= need
                h += 1
                need += 1
            return h

        return max(height(red, blue), height(blue, red))

    def maxHeightOfTriangle_math(self, red: int, blue: int) -> int:
        """
        Interview explanation:
        Odd rows need 1+3+...+ (2k-1)=k^2; even rows need 2+4+...=k(k+1).
        Binary-search max h for each starting color.

        Algorithm:
        - For start=red: odd rows from red, even from blue (and swap).

        Complexity: O(log(red+blue)) time, O(1) space.
        """
        def ok(h: int, a: int, b: int) -> bool:
            # a colors odd rows 1,3,..., b colors even rows 2,4,...
            odd = (h + 1) // 2
            even = h // 2
            return a >= odd * odd and b >= even * (even + 1)

        lo, hi = 0, 200
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid, red, blue) or ok(mid, blue, red):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
