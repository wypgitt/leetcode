#
# @lc app=leetcode id=2910 lang=python3
#
# [2910] Minimum Number of Groups to Create a Valid Assignment
#
# https://leetcode.com/problems/minimum-number-of-groups-to-create-a-valid-assignment/description/
#
# algorithms
# Medium (25.24%)
# Likes:    401
# Dislikes: 189
# Total Accepted:    17.2K
# Total Submissions: 68.2K
# Testcase Example:  "[3,2,3,2,3]"
#
#
# You are given a collection of numbered balls and instructed to sort them
# into boxes for a nearly balanced distribution. There are two rules you
# must follow:
#
# Balls with the same box must have the same value. But, if you have more
# than one ball with the same number, you can put them in different boxes.
#
# The biggest box can only have one more ball than the smallest box.
#
# ​Return the fewest number of boxes to sort these balls following these
# rules.
#
# Example 1:
#
# Input:   balls = [3,2,3,2,3]
#
# Output:   2
#
# Explanation:
#
# We can sort balls into boxes as follows:
#
# [3,3,3]
#
# [2,2]
#
# The size difference between the two boxes doesn't exceed one.
#
# Example 2:
#
# Input:   balls = [10,10,10,3,1,1]
#
# Output:   4
#
# Explanation:
#
# We can sort balls into boxes as follows:
#
# [10]
#
# [10,10]
#
# [3]
#
# [1,1]
#
# You can't use fewer than four boxes while still following the rules. For
# example, putting all three balls numbered 10 in one box would break the
# rule about the maximum size difference between boxes.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def minGroupsForValidAssignment(self, balls: List[int]) -> int:
        """
        Interview explanation:
        Group equal-valued balls into boxes; box sizes differ by at most 1.
        Minimize number of boxes.

        Algorithm:
        - Let freqs be counts per value. Boxes have size s or s+1.
        - Try s from min(freq) down to 1; for each freq f, groups =
          ceil(f/(s+1)); valid iff f >= groups*s. First valid s (largest)
          yields fewest groups.

        Complexity: O(n + min_freq * distinct) time, O(distinct) space.
        """
        freqs = list(Counter(balls).values())
        m = min(freqs)
        for s in range(m, 0, -1):
            groups = 0
            ok = True
            for f in freqs:
                g = (f + s) // (s + 1)  # ceil(f / (s+1))
                if g * s > f:
                    ok = False
                    break
                groups += g
            if ok:
                return groups
        return sum(freqs)
# @lc code=end
