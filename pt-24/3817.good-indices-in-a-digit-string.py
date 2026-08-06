#
# @lc app=leetcode id=3817 lang=python3
#
# [3817] Good Indices in a Digit String
#
# https://leetcode.com/problems/good-indices-in-a-digit-string/description/
#
# algorithms
# Medium (85.42%)
# Likes:    3
# Dislikes: 1
# Total Accepted:    820
# Total Submissions: 960
# Testcase Example:  "\"0234567890112\""
#
#
# You are given a string s consisting of digits.
#
# An index i is called good if there exists a substring of s that ends at
# index i and is equal to the decimal representation of i.
#
# Return an integer array of all good indices in increasing order.
#
# Example 1:
#
# Input: s = "0234567890112"
#
# Output: [0,11,12]
#
# Explanation:​​​​​​​
#
# At index 0, the decimal representation of the index is "0". The
# substring s[0] is "0", which matches, so index 0 is good.
#
# At index 11, the decimal representation is "11". The substring s[10..11]
# is "11", which matches, so index 11 is good.
#
# At index 12, the decimal representation is "12". The substring s[11..12]
# is "12", which matches, so index 12 is good.
#
# No other index has a substring ending at it that equals its decimal
# representation. Therefore, the answer is [0, 11, 12].
#
# Example 2:
#
# Input: s = "01234"
#
# Output: [0,1,2,3,4]
#
# Explanation:
#
# For every index i from 0 to 4, the decimal representation of i is a
# single digit, and the substring s[i] matches that digit.
#
# Therefore, a valid substring ending at each index exists, making all
# indices good.
#
# Example 3:
#
# Input: s = "12345"
#
# Output: []
#
# Explanation:
#
# No index has a substring ending at it that matches its decimal
# representation.
#
# Therefore, there are no good indices and the result is an empty array.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s only consists of digits from '0' to '9'.
#

# @lc code=start

from typing import List


class Solution:
    def goodIndices(self, s: str) -> List[int]:
        """
        Interview explanation:
        Index i is good if some suffix of s[:i+1] equals the decimal string
        of i. Since i < |s| <= 1e5, str(i) has length at most 6.

        Algorithm:
        - For each i, check whether s[i+1-len(str(i)) : i+1] == str(i).

        Complexity: O(n) time, O(1) extra space.
        """
        ans = []
        for i in range(len(s)):
            t = str(i)
            k = len(t)
            if s[i + 1 - k : i + 1] == t:
                ans.append(i)
        return ans
# @lc code=end
