#
# @lc app=leetcode id=1231 lang=python3
#
# [1231] Divide Chocolate
#
# https://leetcode.com/problems/divide-chocolate/description/
#
# algorithms
# Hard (60.63%)
# Likes:    1043
# Dislikes: 78
# Total Accepted:    72.1K
# Total Submissions: 118.9K
# Testcase Example:  "[1,2,3,4,5,6,7,8,9]\n5"
#
#
# You have one chocolate bar that consists of some chunks. Each chunk has
# its own sweetness given by the array sweetness.
#
# You want to share the chocolate with your k friends so you start cutting
# the chocolate bar into k + 1 pieces using k cuts, each piece consists of
# some consecutive chunks.
#
# Being generous, you will eat the piece with the minimum total sweetness
# and give the other pieces to your friends.
#
# Find the maximum total sweetness of the piece you can get by cutting the
# chocolate bar optimally.
#
# Example 1:
#
# Input: sweetness = [1,2,3,4,5,6,7,8,9], k = 5
# Output: 6
# Explanation: You can divide the chocolate to [1,2,3], [4,5], [6], [7],
# [8], [9]
#
# Example 2:
#
# Input: sweetness = [5,6,7,8,9,1,2,3,4], k = 8
# Output: 1
# Explanation: There is only one way to cut the bar into 9 pieces.
#
# Example 3:
#
# Input: sweetness = [1,2,2,1,2,2,1,2,2], k = 2
# Output: 5
# Explanation: You can divide the chocolate to [1,2,2], [1,2,2], [1,2,2]
#
# Constraints:
#
# 0 <= k < sweetness.length <= 10^4
#
# 1 <= sweetness[i] <= 10^5
#
# @lc code=start
from typing import List

class Solution:
    def maximizeSweetness(self, sweetness: List[int], k: int) -> int:
        """
        Interview explanation:
        Premium. Cut into k+1 contiguous pieces; maximize the minimum piece
        sum (your piece is the least sweet). Binary search the minimum
        sweetness; greedily count how many pieces achieve that sum.

        Algorithm:
        - lo=min(sweet), hi=sum/(k+1); check(mid): scan accumulate, count cuts

        Complexity: O(n log S) time, O(1) space.
        """
        def can(mid: int) -> bool:
            total = pieces = 0
            for s in sweetness:
                total += s
                if total >= mid:
                    pieces += 1
                    total = 0
            return pieces >= k + 1

        lo, hi = min(sweetness), sum(sweetness) // (k + 1)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if can(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
