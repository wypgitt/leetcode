#
# @lc app=leetcode id=583 lang=python3
#
# [583] Delete Operation for Two Strings
#
# https://leetcode.com/problems/delete-operation-for-two-strings/description/
#
# algorithms
# Medium (65.52%)
# Likes:    6166
# Dislikes: 93
# Total Accepted:    391.5K
# Total Submissions: 597.4K
# Testcase Example:  '"sea"\n"eat"'
#
# Given two strings word1 and word2, return the minimum number of steps
# required to make word1 and word2 the same.
# 
# In one step, you can delete exactly one character in either string.
# 
# 
# Example 1:
# 
# 
# Input: word1 = "sea", word2 = "eat"
# Output: 2
# Explanation: You need one step to make "sea" to "ea" and another step to make
# "eat" to "ea".
# 
# 
# Example 2:
# 
# 
# Input: word1 = "leetcode", word2 = "etco"
# Output: 4
# 
# 
# 
# Constraints:
# 
# 
# 1 <= word1.length, word2.length <= 500
# word1 and word2 consist of only lowercase English letters.
# 
# 
#

# @lc code=start
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given two strings.  In one operation, we may delete exactly one
        character from either string.

        We need the minimum number of deletions required to make the two strings
        equal.

        Key observation: the final string must be a common subsequence
        --------------------------------------------------------------
        Since we are only allowed to delete characters, we cannot reorder,
        replace, or insert anything.

        Whatever string remains at the end must:

        * appear in `word1` after deleting some characters
        * appear in `word2` after deleting some characters

        That means the final string must be a common subsequence of both words.

        To minimize deletions, we should keep the longest possible common
        subsequence.

        If:

            L = length of the longest common subsequence

        then:

            deletions from word1 = len(word1) - L
            deletions from word2 = len(word2) - L

        Total:

            len(word1) + len(word2) - 2 * L

        So the problem reduces to finding the LCS length.

        DP definition
        -------------
        Let:

            dp[j] = LCS length between the processed prefix of word1
                    and word2[:j]

        We use a rolling one-dimensional DP instead of a full 2D table.

        Full 2D recurrence
        ------------------
        Conceptually:

            lcs[i][j] = LCS length of word1[:i] and word2[:j]

        If the last characters match:

            word1[i - 1] == word2[j - 1]
            lcs[i][j] = lcs[i - 1][j - 1] + 1

        Otherwise:

            lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])

        Space optimization
        ------------------
        Each row only depends on:

        * the previous row, same column: `lcs[i - 1][j]`
        * the current row, previous column: `lcs[i][j - 1]`
        * the previous row, previous column: `lcs[i - 1][j - 1]`

        We store one row in `dp`.

        During the inner loop:

        * `dp[j]` before update is `lcs[i - 1][j]`
        * `dp[j - 1]` after update is `lcs[i][j - 1]`
        * `previous_diagonal` stores `lcs[i - 1][j - 1]`

        Algorithm
        ---------
        1. Make `word2` the shorter string if desired, to reduce memory.
        2. Initialize `dp = [0] * (len(word2) + 1)`.
        3. For each character `char1` in `word1`:
              - keep `previous_diagonal = 0`
              - scan characters of `word2`
              - update LCS values using the recurrence
        4. Let `lcs_length = dp[-1]`.
        5. Return:

               len(word1) + len(word2) - 2 * lcs_length

        Data structure choice
        ---------------------
        We use a list of integers for DP.

        Why:

        * string lengths are up to 500, so O(mn) time is fine
        * a 1D list reduces space from O(mn) to O(min(m, n))
        * integer DP directly represents LCS lengths

        Correctness proof
        -----------------
        Lemma 1: Any final equal string after deletions is a common subsequence
        of `word1` and `word2`.
        Deleting characters preserves the relative order of the remaining
        characters.  Therefore the final string must be obtainable as a
        subsequence from both original strings.

        Lemma 2: If the longest common subsequence has length `L`, at least
        `len(word1) + len(word2) - 2L` deletions are necessary.
        No common final string can be longer than `L`.  If the final string has
        length at most `L`, then at least `len(word1) - L` characters must be
        deleted from `word1` and at least `len(word2) - L` from `word2`.

        Lemma 3: Exactly `len(word1) + len(word2) - 2L` deletions are sufficient.
        Keep one longest common subsequence of length `L` in both strings and
        delete every other character.  Both strings become that same subsequence.

        Lemma 4: The DP computes the LCS length correctly.
        The recurrence is the standard LCS recurrence: matching last characters
        extend the LCS of the two previous prefixes; non-matching last characters
        require dropping one last character from either prefix and taking the
        better result.  The rolling array preserves exactly the previous-row,
        current-row, and diagonal values needed for this recurrence.

        Theorem: The algorithm returns the minimum number of deletions.
        By Lemma 4, the algorithm computes the correct LCS length `L`.  By
        Lemma 2 no solution can use fewer than
        `len(word1) + len(word2) - 2L` deletions.  By Lemma 3 that many deletions
        are achievable.  Therefore the returned value is optimal.

        Complexity analysis
        -------------------
        Let:

            m = len(word1)
            n = len(word2)

        The DP compares every pair of prefixes once.

        Total time:  O(m * n)
        Total space: O(min(m, n))

        Edge cases
        ----------
        * Identical strings:
          LCS length is the full length, so answer is 0.

        * No common characters:
          LCS length is 0, so delete everything from both strings.

        * One string is a subsequence of the other:
          Delete only the extra characters from the longer string.

        * Repeated characters:
          LCS DP handles duplicates correctly because it reasons over positions,
          not just character counts.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              "sea", "eat" -> 2
              "leetcode", "etco" -> 4

        * Equal strings:
              "abc", "abc" -> 0

        * Disjoint strings:
              "abc", "def" -> 6

        * Repeated characters:
              "aabb", "ab" -> 2

        Possible improvement?
        ---------------------
        This is the standard optimal dynamic programming approach for the given
        constraints.  There are bitset optimizations for LCS over small
        alphabets, but O(mn) with m,n <= 500 is simple and comfortably fast.
        """

        if len(word2) > len(word1):
            word1, word2 = word2, word1

        dp = [0] * (len(word2) + 1)

        for char1 in word1:
            previous_diagonal = 0

            for index, char2 in enumerate(word2, start=1):
                previous_row_same_column = dp[index]

                if char1 == char2:
                    dp[index] = previous_diagonal + 1
                else:
                    dp[index] = max(dp[index], dp[index - 1])

                previous_diagonal = previous_row_same_column

        lcs_length = dp[-1]
        return len(word1) + len(word2) - 2 * lcs_length
# @lc code=end
