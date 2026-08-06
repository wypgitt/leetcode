#
# @lc app=leetcode id=522 lang=python3
#
# [522] Longest Uncommon Subsequence II
#
# https://leetcode.com/problems/longest-uncommon-subsequence-ii/description/
#
# algorithms
# Medium (44.81%)
# Likes:    560
# Dislikes: 1395
# Total Accepted:    67.9K
# Total Submissions: 151.5K
# Testcase Example:  '["aba","cdc","eae"]'
#
# Given an array of strings strs, return the length of the longest uncommon
# subsequence between them. If the longest uncommon subsequence does not exist,
# return -1.
# 
# An uncommon subsequence between an array of strings is a string that is a
# subsequence of one string but not the others.
# 
# A subsequence of a string s is a string that can be obtained after deleting
# any number of characters from s.
# 
# 
# For example, "abc" is a subsequence of "aebdc" because you can delete the
# underlined characters in "aebdc" to get "abc". Other subsequences of "aebdc"
# include "aebdc", "aeb", and "" (empty string).
# 
# 
# 
# Example 1:
# Input: strs = ["aba","cdc","eae"]
# Output: 3
# Example 2:
# Input: strs = ["aaa","aaa","aa"]
# Output: -1
# 
# 
# Constraints:
# 
# 
# 2 <= strs.length <= 50
# 1 <= strs[i].length <= 10
# strs[i] consists of lowercase English letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def findLUSlength(self, strs: List[str]) -> int:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        We are given a list of strings.  A string is an uncommon subsequence if:

        * it is a subsequence of one string in the list
        * it is NOT a subsequence of any other string in the list

        We need the maximum possible length of such an uncommon subsequence.
        If none exists, return -1.

        Key observation
        ---------------
        We do not need to generate all subsequences.

        Suppose a string `s` from the input is not a subsequence of any other
        string in the list.  Then `s` itself is an uncommon subsequence, and its
        length is the best possible result coming from that string because no
        subsequence of `s` can be longer than `s`.

        On the other hand, if `s` is a subsequence of another string, then `s`
        itself cannot be uncommon.  Some shorter subsequence of `s` might be
        uncommon, but it cannot beat any valid full input string of length at
        least that much.

        Therefore, checking the input strings themselves is enough:

            answer = longest string that is not a subsequence of any other
                     string

        Why this works with duplicates
        ------------------------------
        If the same string appears twice, then each copy is a subsequence of the
        other copy.  So that string cannot be uncommon as a full string.

        Example:

            ["aaa", "aaa", "aa"]

        The first "aaa" is a subsequence of the second "aaa", and vice versa.
        "aa" is also a subsequence of both "aaa" strings.  No uncommon
        subsequence exists.

        Data structure choice
        ---------------------
        No complex data structure is needed.

        We sort the indices/strings by descending length so we can return as soon
        as we find a valid candidate.  Then we use a two-pointer helper to test
        whether one string is a subsequence of another.

        Subsequence helper
        ------------------
        To test whether `small` is a subsequence of `large`:

        * walk through `large`
        * advance a pointer in `small` whenever characters match
        * if the pointer reaches the end of `small`, then `small` is a
          subsequence

        Algorithm
        ---------
        1. Sort strings by length descending.
        2. For each candidate string `strs[i]` in that order:
              - compare it with every other string `strs[j]`
              - if candidate is a subsequence of any `j != i`, it is not
                uncommon
              - otherwise return its length immediately
        3. If no candidate works, return -1.

        Correctness proof
        -----------------
        Lemma 1: If an input string `s` is not a subsequence of any other input
        string, then `s` is a valid uncommon subsequence.
        It is trivially a subsequence of itself.  Since it is not a subsequence
        of any other string, it satisfies the definition of uncommon.

        Lemma 2: If the longest uncommon subsequence has length `L`, then there
        exists an input string of length at least `L` that is not a subsequence
        of any other input string.
        Let `u` be a longest uncommon subsequence, and suppose `u` is a
        subsequence of input string `s`.  If `s` were a subsequence of another
        string `t`, then by transitivity `u` would also be a subsequence of `t`,
        contradicting that `u` is uncommon.  Therefore `s` is not a subsequence
        of any other string.  Also, `len(s) >= len(u) = L`.

        Lemma 3: The first valid candidate found in descending length order has
        maximum possible uncommon subsequence length.
        The algorithm checks strings from longest to shortest.  By Lemma 1, any
        valid candidate's full length is achievable.  By Lemma 2, no longer
        uncommon subsequence can exist unless there is a longer valid input
        string, which would have been checked earlier.

        Theorem: The algorithm returns the length of the longest uncommon
        subsequence, or -1 if none exists.
        If the algorithm returns a length, Lemma 1 and Lemma 3 show it is
        achievable and optimal.  If it returns -1, every input string is a
        subsequence of some other input string; by Lemma 2, no uncommon
        subsequence can exist.

        Complexity analysis
        -------------------
        Let:

            n = len(strs)
            L = maximum string length

        Sorting costs O(n log n).
        For each pair of strings, subsequence checking costs O(L).

        Total time:  O(n^2 * L)
        Total space: O(n) for sorting/index ordering, or O(1) auxiliary aside
        from Python's sort storage.

        With n <= 50 and L <= 10, this is tiny.

        Edge cases
        ----------
        * Duplicate longest strings:
          A duplicate is a subsequence of the other duplicate, so it is not
          uncommon.

        * A shorter string that is not contained anywhere else:
          It may be the answer if all longer strings fail.

        * All strings mutually covered:
          Return -1.

        * Same lengths but different strings:
          A string of the same length can only be a subsequence of another same
          length string if they are equal.

        Test strategy
        -------------
        Useful tests:

        * Provided examples:
              ["aba","cdc","eae"] -> 3
              ["aaa","aaa","aa"]  -> -1

        * Duplicates plus unique shorter strings.
        * Strings of the same length but different content.
        * One string being a subsequence of a longer string.

        Possible improvement?
        ---------------------
        Because the constraints are very small, this direct pairwise approach is
        ideal.  Counting duplicate strings first can skip some checks, but it is
        not necessary and does not improve the asymptotic bound in a meaningful
        way here.
        """

        def is_subsequence(small: str, large: str) -> bool:
            pointer = 0
            for char in large:
                if pointer < len(small) and small[pointer] == char:
                    pointer += 1
            return pointer == len(small)

        order = sorted(range(len(strs)), key=lambda index: len(strs[index]), reverse=True)

        for index in order:
            candidate = strs[index]
            uncommon = True

            for other_index, other in enumerate(strs):
                if other_index == index:
                    continue

                if len(other) >= len(candidate) and is_subsequence(candidate, other):
                    uncommon = False
                    break

            if uncommon:
                return len(candidate)

        return -1
# @lc code=end
