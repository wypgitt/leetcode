#
# @lc app=leetcode id=1578 lang=python3
#
# [1578] Minimum Time to Make Rope Colorful
#
# https://leetcode.com/problems/minimum-time-to-make-rope-colorful/description/
#
# algorithms
# Medium (65.19%)
# Likes:    4350
# Dislikes: 157
# Total Accepted:    413K
# Total Submissions: 634K
# Testcase Example:  "\"abaac\""
#
# Alice has n balloons arranged on a rope. You are given a 0-indexed string
# colors where colors[i] is the color of the i^th balloon.
#
# Alice wants the rope to be colorful. She does not want two consecutive
# balloons to be of the same color, so she asks Bob for help. Bob can remove
# some balloons from the rope to make it colorful. You are given a 0-indexed
# integer array neededTime where neededTime[i] is the time (in seconds) that
# Bob needs to remove the i^th balloon from the rope.
#
# Return the minimum time Bob needs to make the rope colorful.
#
# Example 1:
#
# Input: colors = "abaac", neededTime = [1,2,3,4,5]
# Output: 3
# Explanation: In the above image, 'a' is blue, 'b' is red, and 'c' is green.
# Bob can remove the blue balloon at index 2. This takes 3 seconds.
# There are no longer two consecutive balloons of the same color. Total time =
# 3.
#
# Example 2:
#
# Input: colors = "abc", neededTime = [1,2,3]
# Output: 0
# Explanation: The rope is already colorful. Bob does not need to remove any
# balloons from the rope.
#
# Example 3:
#
# Input: colors = "aabaa", neededTime = [1,2,3,4,1]
# Output: 2
# Explanation: Bob will remove the balloons at indices 0 and 4. Each balloons
# takes 1 second to remove.
# There are no longer two consecutive balloons of the same color. Total time =
# 1 + 1 = 2.
#
# Constraints:
#
# n == colors.length == neededTime.length
#
# 1 <= n <= 10^5
#
# 1 <= neededTime[i] <= 10^4
#
# colors contains only lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def minCost(self, colors: str, neededTime: List[int]) -> int:
        """
        Interview explanation:
        In each group of consecutive same color, keep the balloon with max
        neededTime and remove the rest (sum - max).

        Algorithm (greedy groups):
        - Walk runs of equal color; accumulate sum and max; add sum-max to ans.

        Complexity: O(n) time, O(1) space.
        """
        ans = i = 0
        n = len(colors)
        while i < n:
            j = i
            total = mx = 0
            while j < n and colors[j] == colors[i]:
                total += neededTime[j]
                mx = max(mx, neededTime[j])
                j += 1
            ans += total - mx
            i = j
        return ans

    def minCost_stack(self, colors: str, neededTime: List[int]) -> int:
        """
        Interview explanation:
        Alternate one-pass: when current equals previous, remove the cheaper
        of the two (add min time) and keep the more expensive as previous.

        Algorithm:
        - ans=0; for i in 1..n-1: if same color: ans+=min(prev,cur); prev=max
          else prev=cur time.

        Complexity: O(n).
        """
        ans = 0
        prev = neededTime[0]
        for i in range(1, len(colors)):
            if colors[i] == colors[i - 1]:
                ans += min(prev, neededTime[i])
                prev = max(prev, neededTime[i])
            else:
                prev = neededTime[i]
        return ans
# @lc code=end

