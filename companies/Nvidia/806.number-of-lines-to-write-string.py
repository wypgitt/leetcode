#
# @lc app=leetcode id=806 lang=python3
#
# [806] Number of Lines To Write String
#
# https://leetcode.com/problems/number-of-lines-to-write-string/description/
#
# algorithms
# Easy (72.98%)
# Likes:    681
# Dislikes: 1355
# Total Accepted:    120K
# Total Submissions: 164K
# Testcase Example:  "[10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10]"
#
# You are given a string s of lowercase English letters and an array widths
# denoting how many pixels wide each lowercase English letter is. Specifically,
# widths[0] is the width of 'a', widths[1] is the width of 'b', and so on.
#
# You are trying to write s across several lines, where each line is no longer
# than 100 pixels. Starting at the beginning of s, write as many letters on the
# first line such that the total width does not exceed 100 pixels. Then, from
# where you stopped in s, continue writing as many letters as you can on the
# second line. Continue this process until you have written all of s.
#
# Return an array result of length 2 where:
#
# result[0] is the total number of lines.
#
# result[1] is the width of the last line in pixels.
#
# Example 1:
#
# Input: widths =
# [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10],
# s = "abcdefghijklmnopqrstuvwxyz"
# Output: [3,60]
# Explanation: You can write s as follows:
# abcdefghij // 100 pixels wide
# klmnopqrst // 100 pixels wide
# uvwxyz // 60 pixels wide
# There are a total of 3 lines, and the last line is 60 pixels wide.
#
# Example 2:
#
# Input: widths =
# [4,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10],
# s = "bbbcccdddaaa"
# Output: [2,4]
# Explanation: You can write s as follows:
# bbbcccdddaa // 98 pixels wide
# a // 4 pixels wide
# There are a total of 2 lines, and the last line is 4 pixels wide.
#
# Constraints:
#
# widths.length == 26
#
# 2 <= widths[i] <= 10
#
# 1 <= s.length <= 1000
#
# s contains only lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def numberOfLines(self, widths: List[int], s: str) -> List[int]:
        """
        Interview explanation:
        Write letters left-to-right with width[letter]; each line holds at most
        100 units. Start a new line when the next letter would overflow.

        Algorithm:
        - lines=1, cur=0; for each char: w=widths[c]; if cur+w>100: lines++, cur=w
          else cur+=w.
        - Return [lines, cur].

        Complexity: O(n) time, O(1) space.
        """
        lines, cur = 1, 0
        for ch in s:
            w = widths[ord(ch) - 97]
            if cur + w > 100:
                lines += 1
                cur = w
            else:
                cur += w
        return [lines, cur]
# @lc code=end
