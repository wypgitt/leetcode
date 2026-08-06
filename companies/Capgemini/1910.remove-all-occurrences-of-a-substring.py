#
# @lc app=leetcode id=1910 lang=python3
#
# [1910] Remove All Occurrences of a Substring
#
# https://leetcode.com/problems/remove-all-occurrences-of-a-substring/description/
#
# algorithms
# Medium (78.63%)
# Likes:    2649
# Dislikes: 90
# Total Accepted:    420K
# Total Submissions: 534K
# Testcase Example:  "\"daabcbaabcbc\""
#
# Given two strings s and part, perform the following operation on s until all
# occurrences of the substring part are removed:
#
# Find the leftmost occurrence of the substring part and remove it from s.
#
# Return s after removing all occurrences of part.
#
# A substring is a contiguous sequence of characters in a string.
#
# Example 1:
#
# Input: s = "daabcbaabcbc", part = "abc"
# Output: "dab"
# Explanation: The following operations are done:
# - s = "daabcbaabcbc", remove "abc" starting at index 2, so s = "dabaabcbc".
# - s = "dabaabcbc", remove "abc" starting at index 4, so s = "dababc".
# - s = "dababc", remove "abc" starting at index 3, so s = "dab".
# Now s has no occurrences of "abc".
#
# Example 2:
#
# Input: s = "axxxxyyyyb", part = "xy"
# Output: "ab"
# Explanation: The following operations are done:
# - s = "axxxxyyyyb", remove "xy" starting at index 4 so s = "axxxyyyb".
# - s = "axxxyyyb", remove "xy" starting at index 3 so s = "axxyyb".
# - s = "axxyyb", remove "xy" starting at index 2 so s = "axyb".
# - s = "axyb", remove "xy" starting at index 1 so s = "ab".
# Now s has no occurrences of "xy".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# 1 <= part.length <= 1000
#
# s and part consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def removeOccurrences(self, s: str, part: str) -> str:
        """
        Interview explanation:
        Repeatedly delete leftmost occurrence of part until none remain.
        Stack simulation: append chars; whenever suffix equals part, pop it.

        Algorithm:
        - Stack of chars; after each push, if len>=m and last m chars == part, pop m.

        Complexity: O(n * m) time, O(n) space.
        """
        m = len(part)
        st = []
        for ch in s:
            st.append(ch)
            if len(st) >= m and "".join(st[-m:]) == part:
                del st[-m:]
        return "".join(st)

    def removeOccurrences_replace(self, s: str, part: str) -> str:
        """
        Interview explanation:
        Alternate: while part in s: s = s.replace(part, "", 1). Clear but slower.

        Algorithm:
        - Loop leftmost replace until gone.

        Complexity: O(n^2 / m) typical string work.
        """
        while part in s:
            s = s.replace(part, "", 1)
        return s
# @lc code=end
