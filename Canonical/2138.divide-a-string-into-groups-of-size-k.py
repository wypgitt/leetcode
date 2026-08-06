#
# @lc app=leetcode id=2138 lang=python3
#
# [2138] Divide a String Into Groups of Size k
#
# https://leetcode.com/problems/divide-a-string-into-groups-of-size-k/description/
#
# algorithms
# Easy (76.90%)
# Likes:    799
# Dislikes: 32
# Total Accepted:    178.6K
# Total Submissions: 232.3K
# Testcase Example:  "\"abcdefghi\"\n3\n\"x\""
#
# A string s can be partitioned into groups of size k using the following
# procedure:
#
#
# The first group consists of the first k characters of the string, the second
# group consists of the next k characters of the string, and so on. Each element
# can be a part of exactly one group.
#
#
# For the last group, if the string does not have k characters remaining, a
# character fill is used to complete the group.
#
# Note that the partition is done so that after removing the fill character from
# the last group (if it exists) and concatenating all the groups in order, the
# resultant string should be s.
#
# Given the string s, the size of each group k and the character fill, return a
# string array denoting the composition of every group s has been divided into,
# using the above procedure.
#
#
#
# Example 1:
#
# Input: s = "abcdefghi", k = 3, fill = "x"
# Output: ["abc","def","ghi"]
# Explanation:
# The first 3 characters "abc" form the first group.
# The next 3 characters "def" form the second group.
# The last 3 characters "ghi" form the third group.
# Since all groups can be completely filled by characters from the string, we do
# not need to use fill.
# Thus, the groups formed are "abc", "def", and "ghi".
#
# Example 2:
#
# Input: s = "abcdefghij", k = 3, fill = "x"
# Output: ["abc","def","ghi","jxx"]
# Explanation:
# Similar to the previous example, we are forming the first three groups "abc",
# "def", and "ghi".
# For the last group, we can only use the character 'j' from the string. To
# complete this group, we add 'x' twice.
# Thus, the 4 groups formed are "abc", "def", "ghi", and "jxx".
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 100
#
#
# s consists of lowercase English letters only.
#
#
# 1 <= k <= 100
#
#
# fill is a lowercase English letter.
#


# @lc code=start
from typing import List


class Solution:
    def divideString(self, s: str, k: int, fill: str) -> List[str]:
        """
        Interview explanation:
        Split s into groups of length k; pad the last group with fill.

        Algorithm:
        - Chunk by k; if last short, pad with fill*(k-len).

        Complexity: O(n) time, O(n) space.
        """
        ans = []
        for i in range(0, len(s), k):
            chunk = s[i:i + k]
            if len(chunk) < k:
                chunk += fill * (k - len(chunk))
            ans.append(chunk)
        return ans
# @lc code=end

