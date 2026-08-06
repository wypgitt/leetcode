#
# @lc app=leetcode id=1417 lang=python3
#
# [1417] Reformat The String
#
# https://leetcode.com/problems/reformat-the-string/description/
#
# algorithms
# Easy (52.17%)
# Likes:    624
# Dislikes: 110
# Total Accepted:    74.4K
# Total Submissions: 143K
# Testcase Example:  "\"a0b1c2\""
#
# You are given an alphanumeric string s. (Alphanumeric string is a string
# consisting of lowercase English letters and digits).
#
# You have to find a permutation of the string where no letter is followed by
# another letter and no digit is followed by another digit. That is, no two
# adjacent characters have the same type.
#
# Return the reformatted string or return an empty string if it is impossible
# to reformat the string.
#
# Example 1:
#
# Input: s = "a0b1c2"
# Output: "0a1b2c"
# Explanation: No two adjacent characters have the same type in "0a1b2c".
# "a0b1c2", "0a1b2c", "0c2a1b" are also valid permutations.
#
# Example 2:
#
# Input: s = "leetcode"
# Output: ""
# Explanation: "leetcode" has only characters so we cannot separate them by
# digits.
#
# Example 3:
#
# Input: s = "1229857369"
# Output: ""
# Explanation: "1229857369" has only digits so we cannot separate them by
# characters.
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of only lowercase English letters and/or digits.
#

# @lc code=start
class Solution:
    def reformat(self, s: str) -> str:
        """
        Interview explanation:
        Reorder so no two adjacent characters are both letters or both digits.
        Split into letters/digits; if count differ by >1 impossible; interleave
        starting with the longer group.

        Algorithm:
        - Partition; if abs(lenL-lenD)>1 return ""; zip longer with shorter.

        Complexity: O(n) time, O(n) space.
        """
        letters = [c for c in s if c.isalpha()]
        digits = [c for c in s if c.isdigit()]
        if abs(len(letters) - len(digits)) > 1:
            return ""
        if len(digits) > len(letters):
            letters, digits = digits, letters
        res = []
        for i in range(len(digits)):
            res.append(letters[i])
            res.append(digits[i])
        if len(letters) > len(digits):
            res.append(letters[-1])
        return "".join(res)

    def reformat_twopointers(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: same partition then two-pointer fill into result array.

        Algorithm:
        - Place from larger group at even indices, smaller at odd.

        Complexity: O(n) time, O(n) space.
        """
        a = [c for c in s if c.isalpha()]
        b = [c for c in s if c.isdigit()]
        if abs(len(a) - len(b)) > 1:
            return ""
        if len(b) > len(a):
            a, b = b, a
        out = [""] * len(s)
        i = j = 0
        for p in range(len(s)):
            if p % 2 == 0:
                out[p] = a[i]
                i += 1
            else:
                out[p] = b[j]
                j += 1
        return "".join(out)
# @lc code=end
