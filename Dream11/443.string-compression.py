#
# @lc app=leetcode id=443 lang=python3
#
# [443] String Compression
#
# https://leetcode.com/problems/string-compression/description/
#
# algorithms
# Medium (60.52%)
# Likes:    6336
# Dislikes: 8954
# Total Accepted:    1.1M
# Total Submissions: 1.9M
# Testcase Example:  "[\"a\",\"a\",\"b\",\"b\",\"c\",\"c\",\"c\"]"
#
# Given an array of characters chars, compress it using the following
# algorithm:
#
# Begin with an empty string s. For each group of consecutive repeating
# characters in chars:
#
# If the group's length is 1, append the character to s.
#
# Otherwise, append the character followed by the group's length.
#
# The compressed string s should not be returned separately, but instead, be
# stored in the input character array chars. Note that group lengths that are
# 10 or longer will be split into multiple characters in chars.
#
# After you are done modifying the input array, return the new length of the
# array.
#
# You must write an algorithm that uses only constant extra space.
#
# Note: The characters in the array beyond the returned length do not matter
# and should be ignored.
#
# Example 1:
#
# Input: chars = ["a","a","b","b","c","c","c"]
# Output: 6
# Explanation: The groups are "aa", "bb", and "ccc". This compresses to
# "a2b2c3".
# After modifying the input array in-place, the first 6 characters of chars
# should be ["a","2","b","2","c","3"].
#
# Example 2:
#
# Input: chars = ["a"]
# Output: 1
# Explanation: The only group is "a", which remains uncompressed since it is a
# single character.
# After modifying the input array in-place, the first character of chars should
# be ["a"].
#
# Example 3:
#
# Input: chars = ["a","b","b","b","b","b","b","b","b","b","b","b","b"]
# Output: 4
# Explanation: The groups are "a" and "bbbbbbbbbbbb". This compresses to
# "ab12".
# After modifying the input array in-place, the first 4 characters of chars
# should be ["a","b","1","2"].
#
# Constraints:
#
# 1 <= chars.length <= 2000
#
# chars[i] is a lowercase English letter, uppercase English letter, digit, or
# symbol.
#

# @lc code=start

from typing import List


class Solution:
    def compress(self, chars: List[str]) -> int:
        """
        Interview explanation:
        In-place run-length encoding: write each group as char + optional count
        digits into the front of the array; return new length.

        Algorithm:
        - Two pointers read/write. For each run of identical chars, write char
          then digit chars of the count if count>1.
        - Return write index as length.

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(chars)
        write = 0
        read = 0
        while read < n:
            ch = chars[read]
            count = 0
            while read < n and chars[read] == ch:
                read += 1
                count += 1
            chars[write] = ch
            write += 1
            if count > 1:
                for d in str(count):
                    chars[write] = d
                    write += 1
        return write
# @lc code=end
