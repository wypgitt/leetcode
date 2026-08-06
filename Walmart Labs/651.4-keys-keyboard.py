#
# @lc app=leetcode id=651 lang=python3
#
# [651] 4 Keys Keyboard
#
# https://leetcode.com/problems/4-keys-keyboard/description/
#
# algorithms
# Medium (56.49%)
# Likes:    747
# Dislikes: 94
# Total Accepted:    36.4K
# Total Submissions: 64.4K
# Testcase Example:  "3"
#
#
# Imagine you have a special keyboard with the following keys:
#
# A: Print one 'A' on the screen.
#
# Ctrl-A: Select the whole screen.
#
# Ctrl-C: Copy selection to buffer.
#
# Ctrl-V: Print buffer on screen appending it after what has already been
# printed.
#
# Given an integer n, return the maximum number of 'A' you can print on
# the screen with at most n presses on the keys.
#
# Example 1:
#
# Input: n = 3
# Output: 3
# Explanation: We can at most get 3 A's on screen by pressing the
# following key sequence:
# A, A, A
#
# Example 2:
#
# Input: n = 7
# Output: 9
# Explanation: We can at most get 9 A's on screen by pressing following
# key sequence:
# A, A, A, Ctrl A, Ctrl C, Ctrl V, Ctrl V
#
# Constraints:
#
# 1 <= n <= 50
#
# @lc code=start

class Solution:
    def maxA(self, n: int) -> int:
        """
        Interview explanation:
        Premium. Keys: A, Ctrl-A, Ctrl-C, Ctrl-V. Max 'A's with n keystrokes.
        Optimal ends with a paste streak after a select-all+copy; DP over last
        copy breakpoint.

        Algorithm:
        - dp[i] = max A's with i strokes.
        - dp[i] = max(dp[i-1]+1, max over j: dp[j]*(i-j-1)) for paste patterns
          where j is when we finished previous content before Ctrl-A,C,V...

        Complexity: O(n^2) time, O(n) space.
        """
        dp = [0] * (n + 1)
        for i in range(1, n + 1):
            dp[i] = dp[i - 1] + 1  # press A
            for j in range(i - 2):
                # after j keys, Ctrl-A, Ctrl-C, then (i-j-2) Ctrl-V
                dp[i] = max(dp[i], dp[j] * (i - j - 1))
        return dp[n]
# @lc code=end
