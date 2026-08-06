#
# @lc app=leetcode id=517 lang=python3
#
# [517] Super Washing Machines
#
# https://leetcode.com/problems/super-washing-machines/description/
#
# algorithms
# Hard (45.09%)
# Likes:    832
# Dislikes: 223
# Total Accepted:    42.5K
# Total Submissions: 94.2K
# Testcase Example:  "[1,0,5]"
#
# You have n super washing machines on a line. Initially, each washing machine
# has some dresses or is empty.
#
# For each move, you could choose any m (1 <= m <= n) washing machines, and
# pass one dress of each washing machine to one of its adjacent washing
# machines at the same time.
#
# Given an integer array machines representing the number of dresses in each
# washing machine from left to right on the line, return the minimum number of
# moves to make all the washing machines have the same number of dresses. If it
# is not possible to do it, return -1.
#
# Example 1:
#
# Input: machines = [1,0,5]
# Output: 3
# Explanation:
# 1st move: 1 0 <-- 5 => 1 1 4
# 2nd move: 1 <-- 1 <-- 4 => 2 1 3
# 3rd move: 2 1 <-- 3 => 2 2 2
#
# Example 2:
#
# Input: machines = [0,3,0]
# Output: 2
# Explanation:
# 1st move: 0 <-- 3 0 => 1 2 0
# 2nd move: 1 2 --> 0 => 1 1 1
#
# Example 3:
#
# Input: machines = [0,2,0]
# Output: -1
# Explanation:
# It's impossible to make all three washing machines have the same number of
# dresses.
#
# Constraints:
#
# n == machines.length
#
# 1 <= n <= 10^4
#
# 0 <= machines[i] <= 10^5
#

# @lc code=start
from typing import List
class Solution:
    def findMinMoves(self, machines: List[int]) -> int:
        """
        Interview explanation:
        Total dresses must be divisible by n. Target = avg per machine. Moves
        equal max(max load to give away from one machine, max |prefix excess|
        that must cross a cut), since one dress moves across an edge per step.

        Algorithm:
        - If sum % n != 0 return -1; avg = sum // n.
        - Track running excess = sum(machines[i]-avg); answer is
          max(machines[i]-avg, |excess|) over all i.

        Complexity: O(n) time, O(1) space.
        """
        total = sum(machines)
        n = len(machines)
        if total % n != 0:
            return -1
        avg = total // n
        ans = 0
        excess = 0
        for m in machines:
            diff = m - avg
            excess += diff
            ans = max(ans, abs(excess), diff)
        return ans
# @lc code=end
