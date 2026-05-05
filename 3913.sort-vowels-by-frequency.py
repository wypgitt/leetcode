#
# @lc app=leetcode id=3913 lang=python3
#
# [3913] Sort Vowels by Frequency
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given a lowercase string s.
#
# Rearrange only the vowels:
#   a, e, i, o, u
#
# Consonants must stay at their original indices.
#
# The vowels should be placed into the existing vowel positions sorted by:
#   1. non-increasing frequency in the whole string
#   2. if frequencies tie, earlier first occurrence in s
#
# Return the modified string.
#
# Example:
#   s = "leetcode"
#   vowels encountered: e, e, o, e
#   frequencies: e = 3, o = 1
#   sorted vowel stream: e, e, e, o
#   put back into vowel positions -> "leetcedo"
#
#
# Key observation
# We are not sorting individual vowel occurrences by their own position.
# We are sorting vowel *letters* by:
#   (-frequency, first_position)
#
# Then each letter contributes all of its copies consecutively.
#
# Example:
#   s = "aeiaaioooa"
#   counts:
#      a = 4
#      o = 3
#      i = 2
#      e = 1
#
# Sorted letters:
#   a, o, i, e
#
# Expanded vowel stream:
#   aaaaoooiie
#
#
# Data structure choice
# The vowel alphabet has only 5 letters, so simple dictionaries are enough:
#
#   count[v] = frequency of vowel v
#   first[v] = first index where vowel v appears
#
# We also keep:
#   chars = list(s)
#
# because Python strings are immutable and we need to replace characters at
# vowel positions.
#
# No heap or large sorting structure is needed. Sorting at most 5 vowels is O(1).
#
#
# Algorithm
# 1. Scan s:
#      - if s[i] is a vowel:
#          count it
#          record first occurrence if not recorded yet
#
# 2. Sort the distinct vowels by:
#      (-count[v], first[v])
#
# 3. Build the sorted vowel stream:
#      for each vowel v in sorted order:
#          append v repeated count[v] times
#
# 4. Scan the original string positions again:
#      whenever position i is a vowel position, replace it with the next
#      character from the sorted vowel stream.
#
# 5. Join and return.
#
#
# Correctness proof
#
# Lemma 1: The algorithm preserves all consonant positions.
# Proof:
# It only writes to indices whose original character is a vowel. Every consonant
# index is skipped during replacement, so it remains unchanged.
#
# Lemma 2: The sorted vowel stream is ordered according to the problem rule.
# Proof:
# Vowels are sorted with key (-frequency, first_position). This places higher
# frequencies first. If frequencies are equal, smaller first occurrence index
# comes first. Expanding each vowel by its count gives exactly all occurrences in
# the required vowel-letter order.
#
# Lemma 3: Placing the sorted vowel stream into vowel positions gives the unique
# string required by the rule.
# Proof:
# The problem only allows rearranging vowels among the original vowel positions.
# Once the ordered sequence of vowels is determined by Lemma 2, filling vowel
# positions from left to right is the only way to realize that sequence while
# leaving consonants fixed.
#
# Theorem: The algorithm returns the correct modified string.
# Proof:
# By Lemma 1, consonants stay fixed. By Lemma 2, the vowels are sorted by the
# required frequency and tie rules. By Lemma 3, they are placed into the string
# correctly. Therefore the returned string satisfies the problem statement.
#
#
# Complexity analysis
#
# Let n = len(s).
#
# Time:
#   - First scan: O(n)
#   - Sorting at most 5 vowels: O(1)
#   - Building/replacing vowel stream: O(n)
# Overall time complexity: O(n).
#
# Space:
#   - chars uses O(n)
#   - vowel stream uses at most O(n)
#   - count and first dictionaries are O(1) because there are only 5 vowels
# Overall space complexity: O(n).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      s = "leetcode" -> "leetcedo"
#
# 2. Example 2:
#      s = "aeiaaioooa" -> "aaaaoooiie"
#
# 3. Equal frequencies:
#      s = "baeiou" -> "baeiou"
#      Every vowel has frequency 1, so first occurrence order is preserved.
#
# 4. No vowels:
#      s = "bcdfg" -> "bcdfg"
#
# 5. One vowel repeated:
#      s = "banana" -> "banana"
#      Only 'a' appears as a vowel, so nothing changes.
#
# 6. Tie with multiple occurrences:
#      If 'a' and 'e' both appear twice, whichever appears first in s comes first
#      in the sorted vowel stream.
#
#
# Edge cases
#
# - String length 1.
# - No vowels at all.
# - All characters are vowels.
# - All vowels have the same frequency.
#
#
# Possible improvements
#
# - Instead of building the full vowel stream, we could keep a pointer into the
#   sorted vowel groups and emit characters lazily. The current version is
#   simpler and still linear.
# - A fixed-size array for vowels would be slightly faster than dictionaries, but
#   dictionaries keep the code clear.
#
# -------------------------------------------------------------------------------

# @lc code=start
from collections import Counter


class Solution:
    def sortVowels(self, s: str) -> str:
        vowels = set("aeiou")
        count = Counter()
        first = {}

        for index, ch in enumerate(s):
            if ch in vowels:
                count[ch] += 1
                if ch not in first:
                    first[ch] = index

        ordered_vowels = sorted(count, key=lambda ch: (-count[ch], first[ch]))
        sorted_stream = []
        for ch in ordered_vowels:
            sorted_stream.extend(ch for _ in range(count[ch]))

        chars = list(s)
        stream_index = 0
        for index, ch in enumerate(chars):
            if ch in vowels:
                chars[index] = sorted_stream[stream_index]
                stream_index += 1

        return "".join(chars)


# @lc code=end
