#
# @lc app=leetcode id=527 lang=python3
#
# [527] Word Abbreviation
#
# https://leetcode.com/problems/word-abbreviation/description/
#
# algorithms
# Hard (62.74%)
# Likes:    405
# Dislikes: 301
# Total Accepted:    33.9K
# Total Submissions: 54K
# Testcase Example:  '["like","god","internal","me","internet","interval","intension","face","intrusion"]'
#
# Given an array of distinct strings words, return the minimal possible
# abbreviations for every word.
# 
# The following are the rules for a string abbreviation:
# 
# 
# The initial abbreviation for each word is: the first character, then the
# number of characters in between, followed by the last character.
# If more than one word shares the same abbreviation, then perform the
# following operation:
# 
# Increase the prefix (characters in the first part) of each of their
# abbreviations by 1.
# 
# For example, say you start with the words ["abcdef","abndef"] both initially
# abbreviated as "a4f". Then, a sequence of operations would be ["a4f","a4f"]
# -> ["ab3f","ab3f"] -> ["abc2f","abn2f"].
# 
# 
# This operation is repeated until every abbreviation is unique.
# 
# 
# At the end, if an abbreviation did not make a word shorter, then keep it as
# the original word.
# 
# 
# 
# Example 1:
# Input: words =
# ["like","god","internal","me","internet","interval","intension","face","intrusion"]
# Output:
# ["l2e","god","internal","me","i6t","interval","inte4n","f2e","intr4n"]
# Example 2:
# Input: words = ["aa","aaa"]
# Output: ["aa","aaa"]
# 
# 
# Constraints:
# 
# 
# 1 <= words.length <= 400
# 2 <= words[i].length <= 400
# words[i] consists of lowercase English letters.
# All the strings of words are unique.
# 
# 
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def wordsAbbreviation(self, words: List[str]) -> List[str]:
        """
        Interview explanation
        =====================

        Restate the problem
        -------------------
        For each word, we need produce its minimal abbreviation.

        A word abbreviation uses:

            prefix + number_of_omitted_middle_characters + last_character

        Example:

            "internal" with prefix length 1 -> "i6l"
            "internal" with prefix length 2 -> "in5l"

        If two words have the same abbreviation, we increase the prefix length
        of all words in that conflict group by 1.  We repeat until all
        abbreviations are unique.

        Finally, if an abbreviation is not shorter than the original word, we
        keep the original word.

        Key observation
        ---------------
        The process described by the problem is naturally simulated:

        * each word has a current prefix length
        * compute all abbreviations
        * find duplicate abbreviations
        * increase prefix length only for words in duplicate groups
        * repeat

        Constraints are small enough:

            number of words <= 400
            word length <= 400

        so this direct simulation is clean and efficient.

        Abbreviation helper
        -------------------
        For a word and prefix length `prefix_length`:

            omitted = len(word) - prefix_length - 1

        The abbreviation candidate is:

            word[:prefix_length] + str(omitted) + word[-1]

        But if this candidate is not shorter than the original word, we return
        the original word instead.

        Why?

            "god" -> "g1d" has length 3, not shorter than "god".

        The problem says to keep the original in that case.

        Data structure choice
        ---------------------
        We use:

        * `prefix_lengths[i]`
          Current prefix length for `words[i]`.

        * `groups`
          A dictionary mapping abbreviation -> list of indices that currently
          produce that abbreviation.

        `defaultdict(list)` is a natural fit because grouping by abbreviation is
        exactly the operation we need each round.

        Algorithm
        ---------
        1. Initialize every prefix length to 1.
        2. Repeat:
              - compute each word's current abbreviation
              - group indices by abbreviation
              - for every group with more than one index:
                    increase each of those words' prefix length by 1
              - if no group has a conflict, stop
        3. Return the final abbreviations.

        Why this produces minimal abbreviations
        ---------------------------------------
        A word's prefix length is increased only when its current abbreviation is
        not unique.  If an abbreviation is already unique, increasing its prefix
        would make it longer for no reason.  Therefore every word stops at the
        first prefix length that makes its abbreviation unique, which is exactly
        minimal under the problem's repeated-conflict rule.

        Correctness proof
        -----------------
        Lemma 1: At every iteration, `groups` correctly identifies exactly which
        words currently share abbreviations.
        The algorithm computes the current abbreviation for every word using its
        current prefix length and inserts the word's index into the dictionary
        under that abbreviation.  Therefore two indices are in the same group if
        and only if their current abbreviations are equal.

        Lemma 2: If a word's current abbreviation is unique, its prefix length
        should not be increased in any minimal solution following the problem's
        operation.
        The operation is triggered only by shared abbreviations.  If a word is
        not in a duplicate group, its current abbreviation already satisfies
        uniqueness relative to all other current abbreviations.  Increasing its
        prefix would only make the abbreviation no shorter and is unnecessary.

        Lemma 3: If a word is in a duplicate group, increasing its prefix length
        by 1 is necessary before the process can finish.
        While two or more words share the same abbreviation, the final condition
        "every abbreviation is unique" is not satisfied.  The problem's stated
        operation for such a group is to increase the prefix length of each word
        in that group by 1.

        Lemma 4: When the algorithm stops, all returned abbreviations are unique.
        The algorithm stops only after building groups and finding no group with
        size greater than 1.  By Lemma 1, that means no two current
        abbreviations are equal.

        Lemma 5: Each returned abbreviation is minimal under the conflict
        resolution process.
        By Lemma 2, the algorithm never increases a prefix length unless the
        word is currently in a conflict.  By Lemma 3, every increase it performs
        is required by the process.  Thus each word stops at the earliest prefix
        length where it is no longer conflicting.

        Theorem: The algorithm returns the required abbreviations.
        By Lemma 4, the final abbreviations are unique.  By Lemma 5, they are
        minimal according to the required process.  The helper also applies the
        final rule that abbreviations no shorter than the original word are
        replaced by the original word.  Therefore the returned list satisfies the
        problem statement.

        Complexity analysis
        -------------------
        Let:

            n = number of words
            L = maximum word length

        In each round, we compute abbreviations for all words.  Building an
        abbreviation can copy up to O(L) characters in the worst case.  A word's
        prefix length can increase at most L times.

        Total time:  O(n * L^2) in the straightforward string-building analysis.

        With n <= 400 and L <= 400, this is easily acceptable.  In practice it is
        fast because most words resolve after few increments.

        Space:

            O(n * L)

        for abbreviation strings and grouping lists in one iteration.

        Edge cases
        ----------
        * Very short words:
          If the abbreviation is not shorter, return the original word.

        * Words with the same first and last character:
          They may conflict for several prefix lengths and are handled by the
          repeated grouping.

        * Words of different lengths:
          Their numbers in the abbreviation differ, so they may already be
          unique.

        * All words distinct but abbreviations collide:
          Prefix lengths increase only for the colliding words.

        Test strategy
        -------------
        Useful tests:

        * Provided examples.
        * Short words like ["aa", "aaa"].
        * Many words sharing a long common prefix.
        * Words that do not conflict at all.
        * Random small cases checked by verifying uniqueness and no abbreviation
          is longer/equal unless returned as the original.

        Possible improvement?
        ---------------------
        A trie can compute the minimum distinguishing prefix within conflict
        classes more directly.  The iterative grouping solution is simpler,
        mirrors the problem statement, and is well within the constraints.
        """

        prefix_lengths = [1] * len(words)

        def abbreviate(word: str, prefix_length: int) -> str:
            omitted = len(word) - prefix_length - 1
            abbreviation = word[:prefix_length] + str(omitted) + word[-1]
            return abbreviation if len(abbreviation) < len(word) else word

        while True:
            groups: dict[str, list[int]] = defaultdict(list)

            for index, word in enumerate(words):
                groups[abbreviate(word, prefix_lengths[index])].append(index)

            has_conflict = False
            for indices in groups.values():
                if len(indices) <= 1:
                    continue

                has_conflict = True
                for index in indices:
                    prefix_lengths[index] += 1

            if not has_conflict:
                break

        return [abbreviate(word, prefix_lengths[index]) for index, word in enumerate(words)]
# @lc code=end
