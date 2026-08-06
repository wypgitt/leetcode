#
# @lc app=leetcode id=2380 lang=python3
#
# [2380] Time Needed to Rearrange a Binary String
#
# https://leetcode.com/problems/time-needed-to-rearrange-a-binary-string/description/
#
# algorithms
# Medium (53.49%)
# Likes:    563
# Dislikes: 118
# Total Accepted:    46.5K
# Total Submissions: 87K
# Testcase Example:  "\"0110101\""
#
# You are given a binary string s. In one second, all occurrences of "01" are
# simultaneously replaced with "10". This process repeats until no occurrences
# of "01" exist.
#
# Return the number of seconds needed to complete this process.
#
#
#
# Example 1:
#
# Input: s = "0110101"
# Output: 4
# Explanation:
# After one second, s becomes "1011010".
# After another second, s becomes "1101100".
# After the third second, s becomes "1110100".
# After the fourth second, s becomes "1111000".
# No occurrence of "01" exists any longer, and the process needed 4 seconds to
# complete,
# so we return 4.
#
# Example 2:
#
# Input: s = "11100"
# Output: 0
# Explanation:
# No occurrence of "01" exists in s, and the processes needed 0 seconds to
# complete,
# so we return 0.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 1000
#
#
# s[i] is either '0' or '1'.
#
#
#
# Follow up:
#
# Can you solve this problem in O(n) time complexity?
#

# @lc code=start

class Solution:
    def secondsToRemoveOccurrences(self, s: str) -> int:
        """
        Interview explanation:
        Each second, simultaneously replace every "01" with "10". Return seconds
        until no "01" left (all 1s left of 0s).

        Algorithm:
        - Track zeros seen; each '1' bubbles left: ans = max(ans+1, zeros).

        Complexity: O(n) time, O(1) space.
        """
        ans = zeros = 0
        for ch in s:
            if ch == '0':
                zeros += 1
            elif zeros:
                ans = max(ans + 1, zeros)
        return ans

    def secondsToRemoveOccurrences_simulate(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: simulate simultaneous "01"->"10" swaps until stable.

        Algorithm:
        - Each second, from a copy of the string, swap all positions where
          chars[i:i+2]=="01" based on the previous state.

        Complexity: O(n^2) time, O(n) space.
        """
        chars = list(s)
        sec = 0
        while True:
            nxt = chars[:]
            changed = False
            for i in range(len(chars) - 1):
                if chars[i] == '0' and chars[i + 1] == '1':
                    nxt[i], nxt[i + 1] = '1', '0'
                    changed = True
            if not changed:
                return sec
            chars = nxt
            sec += 1
# @lc code=end
