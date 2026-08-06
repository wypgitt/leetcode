#
# @lc app=leetcode id=843 lang=python3
#
# [843] Guess the Word
#
# https://leetcode.com/problems/guess-the-word/description/
#
# algorithms
# Hard (36.62%)
# Likes:    1646
# Dislikes: 1878
# Total Accepted:    172K
# Total Submissions: 471K
# Testcase Example:  "\"acckzz\""
#
# You are given an array of unique strings words where words[i] is six letters
# long. One word of words was chosen as a secret word.
#
# You are also given the helper object Master. You may call Master.guess(word)
# where word is a six-letter-long string, and it must be from words.
# Master.guess(word) returns:
#
# -1 if word is not from words, or
#
# an integer representing the number of exact matches (value and position) of
# your guess to the secret word.
#
# There is a parameter allowedGuesses for each test case where allowedGuesses
# is the maximum number of times you can call Master.guess(word).
#
# For each test case, you should call Master.guess with the secret word without
# exceeding the maximum number of allowed guesses. You will get:
#
# "Either you took too many guesses, or you did not find the secret word." if
# you called Master.guess more than allowedGuesses times or if you did not call
# Master.guess with the secret word, or
#
# "You guessed the secret word correctly." if you called Master.guess with the
# secret word with the number of calls to Master.guess less than or equal to
# allowedGuesses.
#
# The test cases are generated such that you can guess the secret word with a
# reasonable strategy (other than using the bruteforce method).
#
# Example 1:
#
# Input: secret = "acckzz", words = ["acckzz","ccbazz","eiowzz","abcczz"],
# allowedGuesses = 10
# Output: You guessed the secret word correctly.
# Explanation:
# master.guess("aaaaaa") returns -1, because "aaaaaa" is not in words.
# master.guess("acckzz") returns 6, because "acckzz" is secret and has all 6
# matches.
# master.guess("ccbazz") returns 3, because "ccbazz" has 3 matches.
# master.guess("eiowzz") returns 2, because "eiowzz" has 2 matches.
# master.guess("abcczz") returns 4, because "abcczz" has 4 matches.
# We made 5 calls to master.guess, and one of them was the secret, so we pass
# the test case.
#
# Example 2:
#
# Input: secret = "hamada", words = ["hamada","khaled"], allowedGuesses = 10
# Output: You guessed the secret word correctly.
# Explanation: Since there are two words, you can guess both.
#
# Constraints:
#
# 1 <= words.length <= 100
#
# words[i].length == 6
#
# words[i] consist of lowercase English letters.
#
# All the strings of words are unique.
#
# secret exists in words.
#
# 10 <= allowedGuesses <= 30
#

# @lc code=start

from typing import List
import random

# """
# This is Master's API interface.
# You should not implement it, or speculate about its implementation
# """
# class Master:
#     def guess(self, word: str) -> int:

# LeetCode provides Master globally. Local stub for py_compile only.
try:
    Master  # type: ignore[name-defined]
except NameError:
    class Master:
        def guess(self, word: str) -> int:
            return -1


class Solution:
    def findSecretWord(self, words: List[str], master: "Master") -> None:
        """
        Interview explanation:
        Minimax / heuristic guessing: pick a word that most evenly partitions
        remaining candidates by match-count buckets; guess; keep only words
        with the same match count vs the guess. Repeat until secret found.

        Algorithm:
        - While candidates: pick guess (minimax or random); matches=master.guess;
          filter candidates with same matches(guess, w).

        Complexity: O(n^2 * L * guesses) time typical, O(n) space.
        """
        def match(a: str, b: str) -> int:
            return sum(x == y for x, y in zip(a, b))

        candidates = words[:]
        for _ in range(10):
            # minimax: choose word minimizing size of largest bucket
            best = None
            best_score = len(candidates) + 1
            for g in candidates:
                buckets = [0] * 7
                for w in candidates:
                    buckets[match(g, w)] += 1
                score = max(buckets)
                if score < best_score:
                    best_score = score
                    best = g
            guess = best if best is not None else candidates[0]
            m = master.guess(guess)
            if m == 6:
                return
            candidates = [w for w in candidates if match(guess, w) == m]

    def findSecretWord_random(self, words: List[str], master: "Master") -> None:
        """
        Interview explanation:
        Simpler classic: randomly guess from remaining candidates and filter
        by match count — often enough within allowedGuesses.

        Algorithm:
        - Random pick; filter by matches; repeat.

        Complexity: O(n * L * guesses) expected, O(n) space.
        """
        def match(a: str, b: str) -> int:
            return sum(x == y for x, y in zip(a, b))

        candidates = words[:]
        for _ in range(10):
            guess = random.choice(candidates)
            m = master.guess(guess)
            if m == 6:
                return
            candidates = [w for w in candidates if match(guess, w) == m]
# @lc code=end
