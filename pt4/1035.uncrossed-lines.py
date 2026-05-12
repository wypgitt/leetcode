#
# @lc app=leetcode id=1035 lang=python3
#
# [1035] Uncrossed Lines
#
# https://leetcode.com/problems/uncrossed-lines/description/
#
# algorithms
# Medium (65.22%)
# Likes:    3978
# Dislikes: 63
# Total Accepted:    196.2K
# Total Submissions: 300.7K
# Testcase Example:  '[1,4,2]\n[1,2,4]'
#
# You are given two integer arrays nums1 and nums2. We write the integers of
# nums1 and nums2 (in the order they are given) on two separate horizontal
# lines.
# 
# We may draw connecting lines: a straight line connecting two numbers nums1[i]
# and nums2[j] such that:
# 
# 
# nums1[i] == nums2[j], and
# the line we draw does not intersect any other connecting (non-horizontal)
# line.
# 
# 
# Note that a connecting line cannot intersect even at the endpoints (i.e.,
# each number can only belong to one connecting line).
# 
# Return the maximum number of connecting lines we can draw in this way.
# 
# 
# Example 1:
# 
# 
# Input: nums1 = [1,4,2], nums2 = [1,2,4]
# Output: 2
# Explanation: We can draw 2 uncrossed lines as in the diagram.
# We cannot draw 3 uncrossed lines, because the line from nums1[1] = 4 to
# nums2[2] = 4 will intersect the line from nums1[2]=2 to nums2[1]=2.
# 
# 
# Example 2:
# 
# 
# Input: nums1 = [2,5,1,2,5], nums2 = [10,5,2,1,5,2]
# Output: 3
# 
# 
# Example 3:
# 
# 
# Input: nums1 = [1,3,7,1,7,5], nums2 = [1,9,2,5,1]
# Output: 2
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums1.length, nums2.length <= 500
# 1 <= nums1[i], nums2[j] <= 2000
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def maxUncrossedLines(self, nums1: List[int], nums2: List[int]) -> int:
        dp = [0] * (len(nums2) + 1)

        for value1 in nums1:
            previous_diagonal = 0
            for j, value2 in enumerate(nums2, 1):
                old_dp_j = dp[j]
                if value1 == value2:
                    dp[j] = previous_diagonal + 1
                else:
                    dp[j] = max(dp[j], dp[j - 1])
                previous_diagonal = old_dp_j

        return dp[-1]
# @lc code=end

"""
Interview Explanation

Core idea:
Uncrossed matching lines are exactly a longest common subsequence problem. If
we match nums1[i] to nums2[j], all future matches must use later indices in
both arrays, which is the LCS ordering constraint.

Algorithm:
Use dynamic programming where dp[j] represents the best LCS length between the
processed prefix of nums1 and nums2[:j]. For each value in nums1:
- Keep previous_diagonal, the old dp[j - 1] from the prior row.
- If values match, extend that diagonal by 1.
- Otherwise, take the best of skipping from nums1 or nums2.

Data structure choice:
A one-dimensional DP array is enough because each row only depends on the
previous row and the current row's left neighbor. This saves space compared
with the full 2D LCS table.

Correctness:
For each pair of prefixes, the optimal solution either matches the last values
if they are equal, or skips one of the last values if they are not. The update
implements exactly that recurrence. Since every non-crossing set of lines is a
common subsequence and every common subsequence can be drawn without crossing,
the LCS length is the answer.

Complexity:
Time is O(m * n). Space is O(n), where n = len(nums2).

Tests and edge cases:
- No common values: DP remains 0.
- All values equal: answer is min(m, n).
- Duplicate values: LCS DP chooses the best ordered pairing.
- One-element arrays work with the same recurrence.
"""
