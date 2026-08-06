#
# @lc app=leetcode id=546 lang=python3
#
# [546] Remove Boxes
#
# https://leetcode.com/problems/remove-boxes/description/
#
# algorithms
# Hard (49.6%)
# Likes:    2499
# Dislikes: 138
# Total Accepted:    65.5K
# Total Submissions: 132K
# Testcase Example:  "[1,3,2,2,2,3,4,3,1]"
#
# You are given several boxes with different colors represented by different
# positive numbers.
#
# You may experience several rounds to remove boxes until there is no box left.
# Each time you can choose some continuous boxes with the same color (i.e.,
# composed of k boxes, k >= 1), remove them and get k * k points.
#
# Return the maximum points you can get.
#
# Example 1:
#
# Input: boxes = [1,3,2,2,2,3,4,3,1]
# Output: 23
# Explanation:
# [1, 3, 2, 2, 2, 3, 4, 3, 1]
# ----> [1, 3, 3, 4, 3, 1] (3*3=9 points)
# ----> [1, 3, 3, 3, 1] (1*1=1 points)
# ----> [1, 1] (3*3=9 points)
# ----> [] (2*2=4 points)
#
# Example 2:
#
# Input: boxes = [1,1,1]
# Output: 9
#
# Example 3:
#
# Input: boxes = [1]
# Output: 1
#
# Constraints:
#
# 1 <= boxes.length <= 100
#
# 1 <= boxes[i] <= 100
#

# @lc code=start
from functools import lru_cache
from typing import List
class Solution:
    def removeBoxes(self, boxes: List[int]) -> int:
        """
        Interview explanation:
        Interval DP with streak: dp(l, r, k) = max points removing boxes[l..r]
        when k extra boxes equal to boxes[r] are already attached on the right.
        Remove the (k+1)-streak of boxes[r] for (k+1)^2, or merge same-color
        boxes inside the interval first.

        Algorithm:
        - Memoized recursion on (l, r, k).
        - Collapse trailing equals into k; try all split points where boxes[m]
          == boxes[r] to attach before removing.

        Complexity: O(n^4) time, O(n^3) space typical for this DP.
        """
        n = len(boxes)

        @lru_cache(None)
        def dp(l: int, r: int, k: int) -> int:
            if l > r:
                return 0
            while l < r and boxes[r - 1] == boxes[r]:
                r -= 1
                k += 1
            # remove boxes[r] together with k same-colored attached
            ans = dp(l, r - 1, 0) + (k + 1) * (k + 1)
            for m in range(l, r):
                if boxes[m] == boxes[r]:
                    ans = max(ans, dp(l, m, k + 1) + dp(m + 1, r - 1, 0))
            return ans

        return dp(0, n - 1, 0)
# @lc code=end

