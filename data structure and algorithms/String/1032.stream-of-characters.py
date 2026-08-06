#
# @lc app=leetcode id=1032 lang=python3
#
# [1032] Stream of Characters
#
# https://leetcode.com/problems/stream-of-characters/description/
#
# algorithms
# Hard (52.69%)
# Likes:    1892
# Dislikes: 187
# Total Accepted:    113K
# Total Submissions: 215K
# Testcase Example:  "[\"StreamChecker\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\",\"query\"]"
#
# Design an algorithm that accepts a stream of characters and checks if a
# suffix of these characters is a string of a given array of strings words.
#
# For example, if words = ["abc", "xyz"] and the stream added the four
# characters (one by one) 'a', 'x', 'y', and 'z', your algorithm should detect
# that the suffix "xyz" of the characters "axyz" matches "xyz" from words.
#
# Implement the StreamChecker class:
#
# StreamChecker(String[] words) Initializes the object with the strings array
# words.
#
# boolean query(char letter) Accepts a new character from the stream and
# returns true if any non-empty suffix from the stream forms a word that is in
# words.
#
# Example 1:
#
# Input
# ["StreamChecker", "query", "query", "query", "query", "query", "query",
# "query", "query", "query", "query", "query", "query"]
# [[["cd", "f", "kl"]], ["a"], ["b"], ["c"], ["d"], ["e"], ["f"], ["g"], ["h"],
# ["i"], ["j"], ["k"], ["l"]]
# Output
# [null, false, false, false, true, false, true, false, false, false, false,
# false, true]
#
# Explanation
# StreamChecker streamChecker = new StreamChecker(["cd", "f", "kl"]);
# streamChecker.query("a"); // return False
# streamChecker.query("b"); // return False
# streamChecker.query("c"); // return False
# streamChecker.query("d"); // return True, because 'cd' is in the wordlist
# streamChecker.query("e"); // return False
# streamChecker.query("f"); // return True, because 'f' is in the wordlist
# streamChecker.query("g"); // return False
# streamChecker.query("h"); // return False
# streamChecker.query("i"); // return False
# streamChecker.query("j"); // return False
# streamChecker.query("k"); // return False
# streamChecker.query("l"); // return True, because 'kl' is in the wordlist
#
# Constraints:
#
# 1 <= words.length <= 2000
#
# 1 <= words[i].length <= 200
#
# words[i] consists of lowercase English letters.
#
# letter is a lowercase English letter.
#
# At most 4 * 10^4 calls will be made to query.
#

# @lc code=start
from typing import List


class StreamChecker:
    def __init__(self, words: List[str]):
        """
        Interview explanation:
        Reverse trie of all words so we can match stream suffixes by walking
        the stream backward from the newest character. Store recent stream
        chars (bounded by max word length).

        Algorithm:
        - Insert each word reversed into trie; mark ends
        - Keep stream list of seen letters (maxlen)

        Complexity: init O(total chars); query O(min(stream, maxLen)).
        """
        self.trie = {}
        self.maxlen = 0
        for w in words:
            node = self.trie
            for ch in reversed(w):
                node = node.setdefault(ch, {})
            node["#"] = True
            self.maxlen = max(self.maxlen, len(w))
        self.stream = []

    def query(self, letter: str) -> bool:
        """
        Interview explanation:
        Append letter; walk trie from newest char backward; if hit end marker
        return True. Stop early if path missing.

        Algorithm:
        - stream.append(letter); walk up to maxlen chars via trie

        Complexity: O(maxlen) time per query, O(total chars) space overall.
        """
        self.stream.append(letter)
        node = self.trie
        for ch in reversed(self.stream[-self.maxlen :]):
            if ch not in node:
                return False
            node = node[ch]
            if "#" in node:
                return True
        return False


# Your StreamChecker object will be instantiated and called as such:
# obj = StreamChecker(words)
# param_1 = obj.query(letter)
# @lc code=end
