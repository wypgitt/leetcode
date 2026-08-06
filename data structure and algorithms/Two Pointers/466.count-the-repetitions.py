#
# @lc app=leetcode id=466 lang=python3
#
# [466] Count The Repetitions
#
# https://leetcode.com/problems/count-the-repetitions/description/
#
# algorithms
# Hard (35.5%)
# Likes:    453
# Dislikes: 370
# Total Accepted:    31.4K
# Total Submissions: 88.5K
# Testcase Example:  "\"acb\""
#
# We define str = [s, n] as the string str which consists of the string s
# concatenated n times.
#
# For example, str == ["abc", 3] =="abcabcabc".
#
# We define that string s1 can be obtained from string s2 if we can remove some
# characters from s2 such that it becomes s1.
#
# For example, s1 = "abc" can be obtained from s2 = "abdbec" based on our
# definition by removing the bolded underlined characters.
#
# You are given two strings s1 and s2 and two integers n1 and n2. You have the
# two strings str1 = [s1, n1] and str2 = [s2, n2].
#
# Return the maximum integer m such that str = [str2, m] can be obtained from
# str1.
#
# Example 1:
#
# Input: s1 = "acb", n1 = 4, s2 = "ab", n2 = 2
# Output: 2
#
# Example 2:
#
# Input: s1 = "acb", n1 = 1, s2 = "acb", n2 = 1
# Output: 1
#
# Constraints:
#
# 1 <= s1.length, s2.length <= 100
#
# s1 and s2 consist of lowercase English letters.
#
# 1 <= n1, n2 <= 10^6
#

# @lc code=start
class Solution:
    def getMaxRepetitions(self, s1: str, n1: int, s2: str, n2: int) -> int:
        """
        Interview explanation:
        Count how many times s2 repeats inside s1*n1, then // n2. Simulate
        matching s2 against successive copies of s1; record (s2_index →
        (s1_count, s2_count)) to detect a cycle and jump ahead.

        Algorithm:
        - For each used s1 block, advance pointer in s2; count completed s2.
        - When s2 index repeats at a block boundary, cycle length known —
          fast-forward remaining blocks.
        - Return total_s2_matches // n2.

        Complexity: O(|s1| * |s2|) time before cycle, O(|s2|) space.
        """
        if n1 == 0:
            return 0
        indexr = {}
        s1cnt = s2cnt = 0
        j = 0
        while s1cnt < n1:
            s1cnt += 1
            for ch in s1:
                if ch == s2[j]:
                    j += 1
                    if j == len(s2):
                        s2cnt += 1
                        j = 0
            if j in indexr:
                prev_s1, prev_s2 = indexr[j]
                cycle_s1 = s1cnt - prev_s1
                cycle_s2 = s2cnt - prev_s2
                remain = n1 - s1cnt
                cycles = remain // cycle_s1
                s1cnt += cycles * cycle_s1
                s2cnt += cycles * cycle_s2
            else:
                indexr[j] = (s1cnt, s2cnt)
        return s2cnt // n2
# @lc code=end
