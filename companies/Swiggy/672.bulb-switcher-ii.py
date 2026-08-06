#
# @lc app=leetcode id=672 lang=python3
#
# [672] Bulb Switcher II
#
# https://leetcode.com/problems/bulb-switcher-ii/description/
#
# algorithms
# Medium (50.12%)
# Likes:    200
# Dislikes: 248
# Total Accepted:    30.6K
# Total Submissions: 61.1K
# Testcase Example:  '1\n1'
#
# There is a room with n bulbs labeled from 1 to n that all are turned on
# initially, and four buttons on the wall. Each of the four buttons has a
# different functionality where:
# 
# 
# Button 1: Flips the status of all the bulbs.
# Button 2: Flips the status of all the bulbs with even labels (i.e., 2, 4,
# ...).
# Button 3: Flips the status of all the bulbs with odd labels (i.e., 1, 3,
# ...).
# Button 4: Flips the status of all the bulbs with a label j = 3k + 1 where k =
# 0, 1, 2, ... (i.e., 1, 4, 7, 10, ...).
# 
# 
# You must make exactly presses button presses in total. For each press, you
# may pick any of the four buttons to press.
# 
# Given the two integers n and presses, return the number of different possible
# statuses after performing all presses button presses.
# 
# 
# Example 1:
# 
# 
# Input: n = 1, presses = 1
# Output: 2
# Explanation: Status can be:
# - [off] by pressing button 1
# - [on] by pressing button 2
# 
# 
# Example 2:
# 
# 
# Input: n = 2, presses = 1
# Output: 3
# Explanation: Status can be:
# - [off, off] by pressing button 1
# - [on, off] by pressing button 2
# - [off, on] by pressing button 3
# 
# 
# Example 3:
# 
# 
# Input: n = 3, presses = 1
# Output: 4
# Explanation: Status can be:
# - [off, off, off] by pressing button 1
# - [on, off, on] by pressing button 2
# - [off, on, off] by pressing button 3
# - [off, on, on] by pressing button 4
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 1000
# 0 <= presses <= 1000
# 
# 
#

# @lc code=start
class Solution:
    def flipLights(self, n: int, presses: int) -> int:
        n = min(n, 6)
        seen = set()
        for mask in range(16):
            bits = mask.bit_count()
            if bits > presses or (presses - bits) % 2:
                continue
            state = []
            for i in range(1, n + 1):
                on = 1
                if mask & 1:
                    on ^= 1
                if mask & 2 and i % 2 == 0:
                    on ^= 1
                if mask & 4 and i % 2 == 1:
                    on ^= 1
                if mask & 8 and i % 3 == 1:
                    on ^= 1
                state.append(on)
            seen.add(tuple(state))
        return len(seen)
# @lc code=end

"""
Interview explanation:
There are only four buttons, and pressing a button twice cancels out, so only the parity of each button matters: 16 masks. A mask is reachable if it uses no more presses than allowed and has the same parity as presses after adding canceling double-presses.

Data structure: a set stores distinct bulb states. Only the first six bulbs matter because all button patterns repeat every lcm(2,3)=6 bulbs.

Edge cases: n is capped at 6 without changing the count. presses=0 allows only the all-on state.

Complexity: constant time and space: at most 16 masks and 6 bulbs are evaluated.
"""
