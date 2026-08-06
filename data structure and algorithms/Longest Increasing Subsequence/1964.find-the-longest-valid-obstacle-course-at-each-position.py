#
# @lc app=leetcode id=1964 lang=python3
#
# [1964] Find the Longest Valid Obstacle Course at Each Position
#
# https://leetcode.com/problems/find-the-longest-valid-obstacle-course-at-each-position/description/
#
# algorithms
# Hard (62.51%)
# Likes:    1915
# Dislikes: 75
# Total Accepted:    70.9K
# Total Submissions: 113K
# Testcase Example:  "[1,2,3,2]"
#
# You want to build some obstacle courses. You are given a 0-indexed integer
# array obstacles of length n, where obstacles[i] describes the height of the
# i^th obstacle.
#
# For every index i between 0 and n - 1 (inclusive), find the length of the
# longest obstacle course in obstacles such that:
#
# You choose any number of obstacles between 0 and i inclusive.
#
# You must include the i^th obstacle in the course.
#
# You must put the chosen obstacles in the same order as they appear in
# obstacles.
#
# Every obstacle (except the first) is taller than or the same height as the
# obstacle immediately before it.
#
# Return an array ans of length n, where ans[i] is the length of the longest
# obstacle course for index i as described above.
#
# Example 1:
#
# Input: obstacles = [1,2,3,2]
# Output: [1,2,3,3]
# Explanation: The longest valid obstacle course at each position is:
# - i = 0: [1], [1] has length 1.
# - i = 1: [1,2], [1,2] has length 2.
# - i = 2: [1,2,3], [1,2,3] has length 3.
# - i = 3: [1,2,3,2], [1,2,2] has length 3.
#
# Example 2:
#
# Input: obstacles = [2,2,1]
# Output: [1,2,1]
# Explanation: The longest valid obstacle course at each position is:
# - i = 0: [2], [2] has length 1.
# - i = 1: [2,2], [2,2] has length 2.
# - i = 2: [2,2,1], [1] has length 1.
#
# Example 3:
#
# Input: obstacles = [3,1,5,6,4,2]
# Output: [1,1,2,3,2,2]
# Explanation: The longest valid obstacle course at each position is:
# - i = 0: [3], [3] has length 1.
# - i = 1: [3,1], [1] has length 1.
# - i = 2: [3,1,5], [3,5] has length 2. [1,5] is also valid.
# - i = 3: [3,1,5,6], [3,5,6] has length 3. [1,5,6] is also valid.
# - i = 4: [3,1,5,6,4], [3,4] has length 2. [1,4] is also valid.
# - i = 5: [3,1,5,6,4,2], [1,2] has length 2.
#
# Constraints:
#
# n == obstacles.length
#
# 1 <= n <= 10^5
#
# 1 <= obstacles[i] <= 10^7
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def longestObstacleCourseAtEachPosition(self, obstacles: List[int]) -> List[int]:
        """
        Interview explanation:
        For each index, longest non-decreasing subsequence ending there.
        Patience sorting / LIS variant with bisect_right.

        Algorithm:
        - Maintain tails of increasing lengths (non-decreasing).
        - For x: i = bisect_right(tails, x); ans=i+1; place x at i.

        Complexity: O(n log n) time, O(n) space.
        """
        tails: List[int] = []
        ans = []
        for x in obstacles:
            i = bisect.bisect_right(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
            ans.append(i + 1)
        return ans

    def longestObstacleCourseAtEachPosition_dp(self, obstacles: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate O(n^2) DP for clarity / small n: dp[i] = 1 + max dp[j] for
        j<i and obstacles[j] <= obstacles[i].

        Algorithm:
        - Nested loops computing LIS-style non-decreasing ending at i.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(obstacles)
        dp = [1] * n
        for i in range(n):
            for j in range(i):
                if obstacles[j] <= obstacles[i]:
                    dp[i] = max(dp[i], dp[j] + 1)
        return dp
# @lc code=end

