#
# @lc app=leetcode id=3816 lang=python3
#
# [3816] Lexicographically Smallest String After Deleting Duplicate Characters
#
#
# --- Interview Notes ---------------------------------------------------------
#
# Problem restatement
# We are given a lowercase string s.
#
# Operation:
#   Choose a letter that appears at least twice in the current string and delete
#   one occurrence of that letter.
#
# We may perform this operation any number of times. Return the lexicographically
# smallest string that can remain.
#
# Example:
#   s = "aaccb"
#
# Possible resulting strings include:
#   "aaccb", "aacb", "accb", "acb"
#
# The lexicographically smallest is:
#   "aacb"
#
#
# Key interpretation
# Since we may delete only duplicate occurrences, we can never delete the last
# occurrence of a character.
#
# Therefore the final string must be a subsequence of s that contains every
# distinct character from s at least once.
#
# Conversely, any subsequence that contains every distinct character at least
# once is reachable: delete exactly the characters not chosen. Every deleted
# occurrence is safe because at least one occurrence of that character remains.
#
# So the problem becomes:
#
#   Find the lexicographically smallest subsequence of s that contains every
#   distinct character from s at least once.
#
# Important difference from the classic "remove duplicate letters":
#   We do NOT need each character exactly once.
#   Keeping extra copies can make the string lexicographically smaller.
#
# Example:
#   s = "aaccb"
#   "acb" contains each distinct character once.
#   But "aacb" is smaller because after the first 'a', another 'a' is smaller
#   than 'c'.
#
#
# Greedy construction
# Build the answer from left to right.
#
# At any point:
#   start = first index in s that we are still allowed to use
#   missing = set of characters not yet included in the answer
#
# We try letters from 'a' to 'z'. For a candidate letter c, take its earliest
# occurrence i >= start.
#
# This choice is feasible if, after choosing i, every still-missing character
# appears somewhere after i.
#
# If c itself was missing, choosing it removes c from missing.
# If c was already included, choosing it is just an extra duplicate, so missing
# stays the same.
#
# The first feasible c in alphabetical order is the next answer character.
#
#
# Why choosing extra duplicates can be correct
# Suppose missing still contains a future larger character, but the current small
# character appears again before that future character's last occurrence.
#
# Keeping the small duplicate makes the answer lexicographically smaller.
#
# Example:
#   s = "abac"
#
# We must include a, b, c.
# After choosing "ab", there is another 'a' before c.
# "abac" is smaller than "abc" because at the third character 'a' < 'c'.
#
# The greedy feasibility check allows that extra 'a' because c still appears
# later.
#
#
# Feasibility test
# Precompute:
#   last[ch] = last index where ch appears
#
# If we choose occurrence i of candidate c:
#   new_missing = missing without c
#
# The choice is feasible iff:
#   for every ch in new_missing, last[ch] > i
#
# because those characters still need to be chosen later.
#
# If new_missing is empty, the choice is automatically feasible and we can stop
# after appending it.
#
#
# Data structure choice
#
# 1. positions[26]
#    positions[c] stores all indices where character c occurs.
#
# 2. ptr[26]
#    ptr[c] points to the first occurrence of c that is >= start.
#    Since start only moves forward, each pointer only moves forward.
#
# 3. missing bitmask
#    A 26-bit mask representing characters not yet included.
#    Removing a character is one bit operation.
#
# These structures make the algorithm O(26 * answer_length + n), which is O(n)
# because the alphabet size is constant.
#
#
# Walkthrough for s = "aaccb"
# Distinct characters are a, c, b.
#
# start = 0, missing = {a,b,c}
#   choose 'a' at index 0: b and c still appear later -> answer "a"
#
# start = 1, missing = {b,c}
#   choose another 'a' at index 1: b and c still appear later -> answer "aa"
#
# start = 2, missing = {b,c}
#   'a' unavailable
#   'b' at index 4 would leave c missing with no later c -> not feasible
#   'c' at index 2 leaves b later -> answer "aac"
#
# start = 3, missing = {b}
#   'b' at index 4 is feasible and smaller than 'c' -> answer "aacb"
#
#
# Correctness proof
#
# Lemma 1: A string is reachable by the allowed deletions iff it is a subsequence
# of s containing every distinct character of s at least once.
# Proof:
# Any deletion sequence preserves relative order, so the result is a subsequence.
# Since the last occurrence of a character can never be deleted, every original
# distinct character remains at least once.
#
# Conversely, take any subsequence that keeps every distinct character. Delete
# all other occurrences. Whenever we delete a character, at least one occurrence
# of that character is still kept, so the deletion is allowed.
#
# Lemma 2: For a candidate occurrence i, the feasibility test is correct.
# Proof:
# Characters already included no longer need future occurrences. If a character
# remains missing after choosing i, it must be chosen later, so it must have an
# occurrence after i. Since last[ch] is the last possible occurrence, this is
# equivalent to last[ch] > i.
#
# Lemma 3: If a candidate character c is feasible, choosing its earliest
# occurrence is at least as good as choosing any later occurrence of c.
# Proof:
# The output character is the same. An earlier occurrence leaves a superset of
# future positions available, so it cannot make future completion worse and may
# make it better.
#
# Lemma 4: At each step, choosing the smallest feasible next character is safe.
# Proof:
# All reachable completions from the current state must choose some feasible next
# character. Lexicographic order is decided by the first position where strings
# differ. Therefore any completion starting with a larger feasible character is
# worse than one starting with the smallest feasible character. By Lemma 3, using
# the earliest occurrence of that character preserves maximum future flexibility.
#
# Theorem: The algorithm returns the lexicographically smallest reachable string.
# Proof:
# By Lemma 1, reachable strings are exactly feasible subsequences containing all
# distinct characters. The algorithm repeatedly applies the safe greedy choice
# from Lemma 4 and stops exactly when no character is missing. By induction over
# output positions, its prefix is lexicographically no larger than the prefix of
# any other feasible result. Hence the final string is the lexicographically
# smallest reachable string.
#
#
# Complexity analysis
#
# Let n = len(s).
#
# Time:
#   - Building positions and last indices: O(n).
#   - For each output character, scan at most 26 candidate letters.
#   - Pointer movements across all scans are O(n) total.
#   - The output length is at most n.
# Overall time complexity: O(26*n), which is O(n).
#
# Space:
#   - positions stores every index once: O(n).
#   - ptr, last, and masks are O(26).
# Overall space complexity: O(n).
#
#
# Tests to discuss in an interview
#
# 1. Example 1:
#      s = "aaccb" -> "aacb"
#
# 2. Single character:
#      s = "z" -> "z"
#
# 3. Classic exact-once answer is not enough:
#      s = "abac" -> "abac", not "abc"
#
# 4. All same character:
#      s = "aaaa" -> "a"
#      Once one 'a' remains, no more deletions are possible.
#
# 5. Already optimal with duplicates:
#      s = "aaab" -> "aaab"
#
# 6. Random brute force:
#      For small strings, enumerate all subsequences that contain every distinct
#      character and compare with this greedy algorithm.
#
#
# Edge cases
#
# - If s has only one distinct character, answer is one copy of it.
# - Equal letters can be kept if they make the prefix smaller, but only while all
#   missing characters remain available later.
# - The algorithm stops as soon as all distinct characters have appeared; adding
#   more trailing characters would only make the string longer with the current
#   answer as a prefix.
#
#
# Possible improvements
#
# - A next-occurrence table can replace position pointers, but it uses O(26*n)
#   memory. Position lists are lighter and still linear.
# - This resembles monotonic-stack duplicate-removal problems, but the ability
#   to keep extra duplicates makes direct stack logic less natural. The greedy
#   "smallest feasible next character" formulation is clearer.
#
# -------------------------------------------------------------------------------

# @lc code=start
class Solution:
    def lexSmallestAfterDeletion(self, s: str) -> str:
        positions = [[] for _ in range(26)]
        for index, ch in enumerate(s):
            positions[ord(ch) - ord("a")].append(index)

        last = [-1] * 26
        missing = 0
        for ch in range(26):
            if positions[ch]:
                last[ch] = positions[ch][-1]
                missing |= 1 << ch

        ptr = [0] * 26
        start = 0
        answer = []

        while missing:
            for ch in range(26):
                pos_list = positions[ch]
                while ptr[ch] < len(pos_list) and pos_list[ptr[ch]] < start:
                    ptr[ch] += 1

                if ptr[ch] == len(pos_list):
                    continue

                index = pos_list[ptr[ch]]
                new_missing = missing & ~(1 << ch)
                if self._can_finish_after(index, new_missing, last):
                    answer.append(chr(ord("a") + ch))
                    start = index + 1
                    missing = new_missing
                    break

        return "".join(answer)

    def _can_finish_after(self, index: int, missing: int, last: list[int]) -> bool:
        for ch in range(26):
            if missing >> ch & 1 and last[ch] <= index:
                return False
        return True


# @lc code=end
