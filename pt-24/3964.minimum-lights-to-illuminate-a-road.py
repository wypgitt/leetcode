#
# @lc app=leetcode id=3964 lang=python3
#
# [3964] Minimum Lights to Illuminate a Road
#
# https://leetcode.com/problems/minimum-lights-to-illuminate-a-road/description/
#
# algorithms
# Medium (38.00%)
# Likes:    73
# Dislikes: 1
# Total Accepted:    26.7K
# Total Submissions: 70.2K
# Testcase Example:  "[0,0,0,0]"
#
#
# You are given an integer array lights of length n, representing
# positions 0 through n - 1 on a road.
#
# For each position i:
#
# If lights[i] = v, where v > 0, there is a working bulb at position i
# that illuminates every position from max(0, i - v) to min(n - 1, i + v),
# inclusive.
#
# If lights[i] = 0, there is no working bulb at position i.
#
# A position is visible if it is illuminated by at least one working bulb.
#
# You may install additional bulbs at any positions. Each additional bulb
# installed at position j illuminates positions from max(0, j - 1) to
# min(n - 1, j + 1), inclusive.
#
# Return the minimum number of additional bulbs required to make every
# position on the road visible.
#
# Example 1:
#
# Input: lights = [0,0,0,0]
#
# Output: 2
#
# Explanation:
#
# One optimal placement is:
#
# Install an additional bulb at position 1, illuminating positions [0, 1,
# 2].
#
# Install an additional bulb at position 3, illuminating positions [2, 3].
#
# Therefore, the minimum number of additional bulbs required is 2.
#
# Example 2:
#
# Input: lights = [0,0,0,2,0]
#
# Output: 1
#
# Explanation:
#
# Since lights[3] = 2, the working bulb at position 3 illuminates
# positions [1, 2, 3, 4].
#
# Installing an additional bulb at position 1 illuminates positions [0, 1,
# 2], making every position visible.
#
# Therefore, the minimum number of additional bulbs required is 1.
#
# Constraints:
#
# 1 <= n == lights.length <= 10^5
#
# 0 <= lights[i] <= n
#

# @lc code=start

class Solution:
    def minLights(self, lights: list[int]) -> int:
        """
        Interview explanation:
        Mark coverage of existing bulbs with a difference array, then greedily
        cover dark gaps: each extra bulb lights 3 consecutive positions.

        Algorithm:
        - Difference-array add +1 on each working bulb's illuminated range.
        - Scan left to right; accumulate coverage and track consecutive dark cells.
        - Each dark run of length L needs ceil(L / 3) extra bulbs.

        Complexity: O(n) time, O(n) space.
        """
        n = len(lights)
        d = [0] * n
        for i, v in enumerate(lights):
            if v > 0:
                l = max(0, i - v)
                r = min(n - 1, i + v)
                d[l] += 1
                if r + 1 < n:
                    d[r + 1] -= 1
        s = cnt = ans = 0
        for x in d:
            s += x
            if s == 0:
                cnt += 1
            else:
                ans += (cnt + 2) // 3
                cnt = 0
        ans += (cnt + 2) // 3
        return ans
# @lc code=end
