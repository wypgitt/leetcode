#
# @lc app=leetcode id=158 lang=python3
#
# [158] Read N Characters Given read4 II - Call Multiple Times
#
# https://leetcode.com/problems/read-n-characters-given-read4-ii-call-multiple-times/description/
#
# algorithms
# Hard (43.34%)
# Likes:    889
# Dislikes: 1821
# Total Accepted:    197.7K
# Total Submissions: 456.1K
# Testcase Example:  "\"abc\"\n[1,2,1]"
#
#
# Given a file and assume that you can only read the file using a given
# method read4, implement a method read to read n characters. Your method
# read may be called multiple times.
#
# Method read4:
#
# The API read4 reads four consecutive characters from file, then writes
# those characters into the buffer array buf4.
#
# The return value is the number of actual characters read.
#
# Note that read4() has its own file pointer, much like FILE *fp in C.
#
# Definition of read4:
#
#     Parameter:  char[] buf4
#     Returns:    int
#
# buf4[] is a destination, not a source. The results from read4 will be
# copied to buf4[].
#
# Below is a high-level example of how read4 works:
#
# File file("abcde"); // File is "abcde", initially file pointer (fp)
# points to 'a'
# char[] buf4 = new char[4]; // Create buffer with enough space to store
# characters
# read4(buf4); // read4 returns 4. Now buf4 = "abcd", fp points to 'e'
# read4(buf4); // read4 returns 1. Now buf4 = "e", fp points to end of
# file
# read4(buf4); // read4 returns 0. Now buf4 = "", fp points to end of file
#
# Method read:
#
# By using the read4 method, implement the method read that reads n
# characters from file and store it in the buffer array buf. Consider that
# you cannot manipulate file directly.
#
# The return value is the number of actual characters read.
#
# Definition of read:
#
#     Parameters: char[] buf, int n
#     Returns:    int
#
# buf[] is a destination, not a source. You will need to write the results
# to buf[].
#
# Note:
#
# Consider that you cannot manipulate the file directly. The file is only
# accessible for read4 but not for read.
#
# The read function may be called multiple times.
#
# Please remember to RESET your class variables declared in Solution, as
# static/class variables are persisted across multiple test cases. Please
# see here for more details.
#
# You may assume the destination buffer array, buf, is guaranteed to have
# enough space for storing n characters.
#
# It is guaranteed that in a given test case the same buffer buf is called
# by read.
#
# Example 1:
#
# Input: file = "abc", queries = [1,2,1]
# Output: [1,2,0]
# Explanation: The test case represents the following scenario:
# File file("abc");
# Solution sol;
# sol.read(buf, 1); // After calling your read method, buf should contain
# "a". We read a total of 1 character from the file, so return 1.
# sol.read(buf, 2); // Now buf should contain "bc". We read a total of 2
# characters from the file, so return 2.
# sol.read(buf, 1); // We have reached the end of file, no more characters
# can be read. So return 0.
# Assume buf is allocated and guaranteed to have enough space for storing
# all characters from the file.
#
# Example 2:
#
# Input: file = "abc", queries = [4,1]
# Output: [3,0]
# Explanation: The test case represents the following scenario:
# File file("abc");
# Solution sol;
# sol.read(buf, 4); // After calling your read method, buf should contain
# "abc". We read a total of 3 characters from the file, so return 3.
# sol.read(buf, 1); // We have reached the end of file, no more characters
# can be read. So return 0.
#
# Constraints:
#
# 1 <= file.length <= 500
#
# file consist of English letters and digits.
#
# 1 <= queries.length <= 10
#
# 1 <= queries[i] <= 500
#
# @lc code=start
from typing import List

# The read4 API is already defined for you.
# def read4(buf4: List[str]) -> int:


class Solution:
    def __init__(self):
        """
        Interview explanation:
        Persist a 4-char read4 buffer across multiple read() calls so leftover
        characters from a previous call are not lost.

        Algorithm:
        - _buf4 holds the last read4 chunk; _buf4_size is valid length;
          _buf4_ptr is the next unread index within that chunk.

        Complexity: O(1) space for the persistent buffer.
        """
        self._buf4 = [""] * 4
        self._buf4_size = 0
        self._buf4_ptr = 0

    def read(self, buf: List[str], n: int) -> int:
        """
        Interview explanation:
        Multiple read() calls must preserve leftover characters from a prior
        read4. Keep an internal 4-char buffer with size and pointer across calls.

        Algorithm:
        - While still needing characters:
          - If internal buffer exhausted, refill via read4; stop on EOF.
          - Copy from internal buffer into buf until need is satisfied or
            internal buffer ends.
        - Return number of characters delivered this call.

        Complexity: O(n) time per call, O(1) persistent buffer space.
        """
        copied = 0
        while copied < n:
            if self._buf4_ptr >= self._buf4_size:
                self._buf4_size = read4(self._buf4)
                self._buf4_ptr = 0
                if self._buf4_size == 0:
                    break
            buf[copied] = self._buf4[self._buf4_ptr]
            self._buf4_ptr += 1
            copied += 1
        return copied
# @lc code=end
