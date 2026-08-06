#
# @lc app=leetcode id=925 lang=python3
#
# [925] Long Pressed Name
#
# https://leetcode.com/problems/long-pressed-name/description/
#
# algorithms
# Easy (33.05%)
# Likes:    2617
# Dislikes: 414
# Total Accepted:    200K
# Total Submissions: 606K
# Testcase Example:  "\"alex\""
#
# Your friend is typing his name into a keyboard. Sometimes, when typing a
# character c, the key might get long pressed, and the character will be typed
# 1 or more times.
#
# You examine the typed characters of the keyboard. Return True if it is
# possible that it was your friends name, with some characters (possibly none)
# being long pressed.
#
# Example 1:
#
# Input: name = "alex", typed = "aaleex"
# Output: true
# Explanation: 'a' and 'e' in 'alex' were long pressed.
#
# Example 2:
#
# Input: name = "saeed", typed = "ssaaedd"
# Output: false
# Explanation: 'e' must have been pressed twice, but it was not in the typed
# output.
#
# Constraints:
#
# 1 <= name.length, typed.length <= 1000
#
# name and typed consist of only lowercase English letters.
#

# @lc code=start
class Solution:
    def isLongPressedName(self, name: str, typed: str) -> bool:
        """
        Interview explanation:
        Two pointers: typed may stretch runs of name. Walk name; each char must
        match typed, then consume extra identical presses in typed.

        Algorithm (two pointers):
        - i=j=0
        - While i < len(name): if typed exhausted or mismatch → False
          else advance both; while typed continues same char (and next name
          differs or name done), advance j
        - Also ensure no leftover non-matching typed chars (all leftover must
          equal last name char — handled by requiring j == len(typed) at end
          after consuming extras)

        Complexity: O(n+m) time, O(1) space.
        """
        i = 0
        n, m = len(name), len(typed)
        for j in range(m):
            if i < n and name[i] == typed[j]:
                i += 1
            elif j == 0 or typed[j] != typed[j - 1]:
                return False
        return i == n

    def isLongPressedName_groupby(self, name: str, typed: str) -> bool:
        """
        Interview explanation:
        Alternate: compare run-length encodings; same letters, typed runs >= name.

        Algorithm:
        - Group consecutive chars in both; zip groups and check letter equal
          and typed_count >= name_count; lengths of group lists equal.

        Complexity: O(n+m) time, O(n+m) space.
        """
        from itertools import groupby

        def runs(s: str):
            return [(ch, sum(1 for _ in g)) for ch, g in groupby(s)]

        a, b = runs(name), runs(typed)
        if len(a) != len(b):
            return False
        return all(ca == cb and xa <= xb for (ca, xa), (cb, xb) in zip(a, b))
# @lc code=end

