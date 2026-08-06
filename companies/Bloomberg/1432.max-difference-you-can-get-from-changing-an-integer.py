#
# @lc app=leetcode id=1432 lang=python3
#
# [1432] Max Difference You Can Get From Changing an Integer
#
# https://leetcode.com/problems/max-difference-you-can-get-from-changing-an-integer/description/
#
# algorithms
# Medium (48.63%)
# Likes:    605
# Dislikes: 377
# Total Accepted:    115K
# Total Submissions: 236K
# Testcase Example:  "555"
#
# You are given an integer num. You will apply the following steps to num two
# separate times:
#
# Pick a digit x (0 <= x <= 9).
#
# Pick another digit y (0 <= y <= 9). Note y can be equal to x.
#
# Replace all the occurrences of x in the decimal representation of num by y.
#
# Let a and b be the two results from applying the operation to num
# independently.
#
# Return the max difference between a and b.
#
# Note that neither a nor b may have any leading zeros, and must not be 0.
#
# Example 1:
#
# Input: num = 555
# Output: 888
# Explanation: The first time pick x = 5 and y = 9 and store the new integer in
# a.
# The second time pick x = 5 and y = 1 and store the new integer in b.
# We have now a = 999 and b = 111 and max difference = 888
#
# Example 2:
#
# Input: num = 9
# Output: 8
# Explanation: The first time pick x = 9 and y = 9 and store the new integer in
# a.
# The second time pick x = 9 and y = 1 and store the new integer in b.
# We have now a = 9 and b = 1 and max difference = 8
#
# Constraints:
#
# 1 <= num <= 10^8
#

# @lc code=start
class Solution:
    def maxDiff(self, num: int) -> int:
        """
        Interview explanation:
        Replace all occurrences of one digit d with another digit to maximize
        a-b after two independent mappings (a max, b min, no leading zero).
        Max: replace first non-9 digit with 9. Min: if leading digit!=1 replace
        with 1; else replace first non-0/1 digit with 0.

        Algorithm:
        - s=str(num); build a and b via digit mapping rules; return int(a)-int(b)

        Complexity: O(d) time for d digits, O(d) space.
        """
        s = str(num)

        # maximize
        a = s
        for ch in s:
            if ch != "9":
                a = s.replace(ch, "9")
                break

        # minimize
        b = s
        if s[0] != "1":
            b = s.replace(s[0], "1")
        else:
            for ch in s[1:]:
                if ch not in "01":
                    b = s.replace(ch, "0")
                    break
        return int(a) - int(b)

    def maxDiff_brutemap(self, num: int) -> int:
        """
        Interview explanation:
        Alternate: try all digit→digit maps for max and min candidates (small).

        Algorithm:
        - For x,y in 0..9 map digit x→y (skip invalid leading 0); track max-min.

        Complexity: O(100 * d) time.
        """
        s = str(num)
        vals = []
        for x in range(10):
            for y in range(10):
                t = "".join(str(y) if ch == str(x) else ch for ch in s)
                if t[0] == "0":
                    continue
                vals.append(int(t))
        return max(vals) - min(vals)
# @lc code=end
