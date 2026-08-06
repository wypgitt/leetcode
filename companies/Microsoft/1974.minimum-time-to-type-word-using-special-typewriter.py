#
# @lc app=leetcode id=1974 lang=python3
#
# [1974] Minimum Time to Type Word Using Special Typewriter
#
# https://leetcode.com/problems/minimum-time-to-type-word-using-special-typewriter/description/
#
# algorithms
# Easy (78.86%)
# Likes:    805
# Dislikes: 38
# Total Accepted:    69.8K
# Total Submissions: 88.5K
# Testcase Example:  "\"abc\""
#
# There is a special typewriter with lowercase English letters 'a' to 'z'
# arranged in a circle with a pointer. A character can only be typed if the
# pointer is pointing to that character. The pointer is initially pointing to
# the character 'a'.
#
# Each second, you may perform one of the following operations:
#
# Move the pointer one character counterclockwise or clockwise.
#
# Type the character the pointer is currently on.
#
# Given a string word, return the minimum number of seconds to type out the
# characters in word.
#
# Example 1:
#
# Input: word = "abc"
# Output: 5
# Explanation:
# The characters are printed as follows:
# - Type the character 'a' in 1 second since the pointer is initially on 'a'.
# - Move the pointer clockwise to 'b' in 1 second.
# - Type the character 'b' in 1 second.
# - Move the pointer clockwise to 'c' in 1 second.
# - Type the character 'c' in 1 second.
#
# Example 2:
#
# Input: word = "bza"
# Output: 7
# Explanation:
# The characters are printed as follows:
# - Move the pointer clockwise to 'b' in 1 second.
# - Type the character 'b' in 1 second.
# - Move the pointer counterclockwise to 'z' in 2 seconds.
# - Type the character 'z' in 1 second.
# - Move the pointer clockwise to 'a' in 1 second.
# - Type the character 'a' in 1 second.
#
# Example 3:
#
# Input: word = "zjpc"
# Output: 34
# Explanation:
# The characters are printed as follows:
# - Move the pointer counterclockwise to 'z' in 1 second.
# - Type the character 'z' in 1 second.
# - Move the pointer clockwise to 'j' in 10 seconds.
# - Type the character 'j' in 1 second.
# - Move the pointer clockwise to 'p' in 6 seconds.
# - Type the character 'p' in 1 second.
# - Move the pointer counterclockwise to 'c' in 13 seconds.
# - Type the character 'c' in 1 second.
#
# Constraints:
#
# 1 <= word.length <= 100
#
# word consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def minTimeToType(self, word: str) -> int:
        """
        Interview explanation:
        Typewriter circle a..z; from previous letter move min clockwise /
        counterclockwise, then type (+1). Start at 'a'.

        Algorithm:
        - prev='a'; for c: ans += min(|c-prev|, 26-|c-prev|) + 1; prev=c.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        prev = "a"
        for c in word:
            d = abs(ord(c) - ord(prev))
            ans += min(d, 26 - d) + 1
            prev = c
        return ans

    def minTimeToType_mod(self, word: str) -> int:
        """
        Interview explanation:
        Alternate same circular distance using modular arithmetic on 0..25.

        Algorithm:
        - idx letters; dist = min((a-b)%26, (b-a)%26) + 1 type.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        cur = 0
        for c in word:
            nxt = ord(c) - ord("a")
            dist = (nxt - cur) % 26
            ans += min(dist, 26 - dist) + 1
            cur = nxt
        return ans
# @lc code=end

