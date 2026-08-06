#
# @lc app=leetcode id=1208 lang=python3
#
# [1208] Get Equal Substrings Within Budget
#
# https://leetcode.com/problems/get-equal-substrings-within-budget/description/
#
# algorithms
# Medium (59.98%)
# Likes:    1945
# Dislikes: 151
# Total Accepted:    209K
# Total Submissions: 348K
# Testcase Example:  "\"abcd\""
#
# You are given two strings s and t of the same length and an integer maxCost.
#
# You want to change s to t. Changing the i^th character of s to i^th character
# of t costs |s[i] - t[i]| (i.e., the absolute difference between the ASCII
# values of the characters).
#
# Return the maximum length of a substring of s that can be changed to be the
# same as the corresponding substring of t with a cost less than or equal to
# maxCost. If there is no substring from s that can be changed to its
# corresponding substring from t, return 0.
#
# Example 1:
#
# Input: s = "abcd", t = "bcdf", maxCost = 3
# Output: 3
# Explanation: "abc" of s can change to "bcd".
# That costs 3, so the maximum length is 3.
#
# Example 2:
#
# Input: s = "abcd", t = "cdef", maxCost = 3
# Output: 1
# Explanation: Each character in s costs 2 to change to character in t, so the
# maximum length is 1.
#
# Example 3:
#
# Input: s = "abcd", t = "acde", maxCost = 0
# Output: 1
# Explanation: You cannot make any change, so the maximum length is 1.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# t.length == s.length
#
# 0 <= maxCost <= 10^6
#
# s and t consist of only lowercase English letters.
#



# @lc code=start
class Solution:
    def equalSubstring(self, s: str, t: str, maxCost: int) -> int:
        """
        Interview explanation:
        Cost of changing s[i] to t[i] is |s[i]-t[i]|. Longest substring with
        total cost <= maxCost → classic sliding window.

        Algorithm:
        - Expand right adding cost; while cost > maxCost shrink left; track max len

        Complexity: O(n) time, O(1) space.
        """
        n = len(s)
        cost = left = ans = 0
        for right in range(n):
            cost += abs(ord(s[right]) - ord(t[right]))
            while cost > maxCost:
                cost -= abs(ord(s[left]) - ord(t[left]))
                left += 1
            ans = max(ans, right - left + 1)
        return ans

    def equalSubstring_binary(self, s: str, t: str, maxCost: int) -> int:
        """
        Interview explanation:
        Alternate: prefix costs + binary search maximum length L where some
        window of length L has cost <= maxCost.

        Algorithm:
        - pref[i+1]=pref[i]+|s[i]-t[i]|
        - binary search L; check exists i with pref[i+L]-pref[i] <= maxCost

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(s)
        pref = [0] * (n + 1)
        for i in range(n):
            pref[i + 1] = pref[i] + abs(ord(s[i]) - ord(t[i]))

        def ok(L: int) -> bool:
            for i in range(n - L + 1):
                if pref[i + L] - pref[i] <= maxCost:
                    return True
            return False

        lo, hi = 0, n
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
