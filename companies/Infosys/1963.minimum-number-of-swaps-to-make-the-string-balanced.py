#
# @lc app=leetcode id=1963 lang=python3
#
# [1963] Minimum Number of Swaps to Make the String Balanced
#
# https://leetcode.com/problems/minimum-number-of-swaps-to-make-the-string-balanced/description/
#
# algorithms
# Medium (78.03%)
# Likes:    2584
# Dislikes: 152
# Total Accepted:    252K
# Total Submissions: 323K
# Testcase Example:  "\"][][\""
#
# You are given a 0-indexed string s of even length n. The string consists of
# exactly n / 2 opening brackets '[' and n / 2 closing brackets ']'.
#
# A string is called balanced if and only if:
#
# It is the empty string, or
#
# It can be written as AB, where both A and B are balanced strings, or
#
# It can be written as [C], where C is a balanced string.
#
# You may swap the brackets at any two indices any number of times.
#
# Return the minimum number of swaps to make s balanced.
#
# Example 1:
#
# Input: s = "][]["
# Output: 1
# Explanation: You can make the string balanced by swapping index 0 with index
# 3.
# The resulting string is "[[]]".
#
# Example 2:
#
# Input: s = "]]][[["
# Output: 2
# Explanation: You can do the following to make the string balanced:
# - Swap index 0 with index 4. s = "[]][][".
# - Swap index 1 with index 5. s = "[[][]]".
# The resulting string is "[[][]]".
#
# Example 3:
#
# Input: s = "[]"
# Output: 0
# Explanation: The string is already balanced.
#
# Constraints:
#
# n == s.length
#
# 2 <= n <= 10^6
#
# n is even.
#
# s[i] is either '[' or ']'.
#
# The number of opening brackets '[' equals n / 2, and the number of closing
# brackets ']' equals n / 2.
#

# @lc code=start
class Solution:
    def minSwaps(self, s: str) -> int:
        """
        Interview explanation:
        Balance brackets by swapping. Track unmatched ']' imbalance; each swap
        fixes two unmatched. Answer is (max_imbalance + 1)//2.

        Algorithm:
        - bal=0, mx=0; for c: bal += 1 if '[' else -1; if bal<0 track -bal...
        - Simpler: count extra closing; ans = (extra+1)//2 after scanning.

        Complexity: O(n) time, O(1) space.
        """
        bal = 0
        need = 0
        for c in s:
            if c == "[":
                bal += 1
            else:
                bal -= 1
            if bal < 0:
                need = max(need, -bal)
        return (need + 1) // 2

    def minSwaps_stack(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: strip matched pairs with a stack/counter; unmatched closers
        require (cnt+1)//2 swaps.

        Algorithm:
        - open count; on ']' if open>0 decrement else unmatched++.
        - return (unmatched+1)//2.

        Complexity: O(n) time, O(1) space.
        """
        open_cnt = 0
        unmatched = 0
        for c in s:
            if c == "[":
                open_cnt += 1
            elif open_cnt:
                open_cnt -= 1
            else:
                unmatched += 1
        return (unmatched + 1) // 2
# @lc code=end

