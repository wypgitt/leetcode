#
# @lc app=leetcode id=1804 lang=python3
#
# [1804] Implement Trie II (Prefix Tree)
#
# https://leetcode.com/problems/implement-trie-ii-prefix-tree/description/
#
# algorithms
# Medium (63.57%)
# Likes:    357
# Dislikes: 19
# Total Accepted:    28.1K
# Total Submissions: 44.1K
# Testcase Example:  "[\"Trie\",\"insert\",\"insert\",\"countWordsEqualTo\",\"countWordsStartingWith\",\"erase\",\"countWordsEqualTo\",\"countWordsStartingWith\",\"erase\",\"countWordsStartingWith\"]\n[[],[\"apple\"],[\"apple\"],[\"apple\"],[\"app\"],[\"apple\"],[\"apple\"],[\"app\"],[\"apple\"],[\"app\"]]"
#
#
# A trie (pronounced as "try") or prefix tree is a tree data structure
# used to efficiently store and retrieve keys in a dataset of strings.
# There are various applications of this data structure, such as
# autocomplete and spellchecker.
#
# Implement the Trie class:
#
# Trie() Initializes the trie object.
#
# void insert(String word) Inserts the string word into the trie.
#
# int countWordsEqualTo(String word) Returns the number of instances of
# the string word in the trie.
#
# int countWordsStartingWith(String prefix) Returns the number of strings
# in the trie that have the string prefix as a prefix.
#
# void erase(String word) Erases the string word from the trie.
#
# Example 1:
#
# Input
# ["Trie", "insert", "insert", "countWordsEqualTo",
# "countWordsStartingWith", "erase", "countWordsEqualTo",
# "countWordsStartingWith", "erase", "countWordsStartingWith"]
# [[], ["apple"], ["apple"], ["apple"], ["app"], ["apple"], ["apple"],
# ["app"], ["apple"], ["app"]]
# Output
# [null, null, null, 2, 2, null, 1, 1, null, 0]
#
# Explanation
# Trie trie = new Trie();
# trie.insert("apple");               // Inserts "apple".
# trie.insert("apple");               // Inserts another "apple".
# trie.countWordsEqualTo("apple");    // There are two instances of
# "apple" so return 2.
# trie.countWordsStartingWith("app"); // "app" is a prefix of "apple" so
# return 2.
# trie.erase("apple");                // Erases one "apple".
# trie.countWordsEqualTo("apple");    // Now there is only one instance of
# "apple" so return 1.
# trie.countWordsStartingWith("app"); // return 1
# trie.erase("apple");                // Erases "apple". Now the trie is
# empty.
# trie.countWordsStartingWith("app"); // return 0
#
# Constraints:
#
# 1 <= word.length, prefix.length <= 2000
#
# word and prefix consist only of lowercase English letters.
#
# At most 3 * 10^4 calls in total will be made to insert,
# countWordsEqualTo, countWordsStartingWith, and erase.
#
# It is guaranteed that for any function call to erase, the string word
# will exist in the trie.
#
# @lc code=start
class Trie:
    def __init__(self):
        """
        Interview explanation:
        Trie II: support insert, erase, countWordsEqualTo, countWordsStartingWith.
        Track both word-end counts and prefix pass counts on each node.

        Algorithm:
        - Node: children dict/array, cnt (words ending), pref (words through node).

        Complexity: O(1) init.
        """
        self.children = {}
        self.cnt = 0
        self.pref = 0

    def insert(self, word: str) -> None:
        """
        Interview explanation:
        Insert word; increment pref along path and cnt at terminal.

        Algorithm:
        - Walk/create nodes; each node.pref += 1; terminal.cnt += 1.

        Complexity: O(L) time, O(L) space.
        """
        node = self
        for ch in word:
            if ch not in node.children:
                node.children[ch] = Trie()
            node = node.children[ch]
            node.pref += 1
        node.cnt += 1

    def countWordsEqualTo(self, word: str) -> int:
        """
        Interview explanation:
        Return how many times word was inserted and not erased.

        Algorithm:
        - Walk word; return terminal.cnt or 0 if missing.

        Complexity: O(L).
        """
        node = self
        for ch in word:
            if ch not in node.children:
                return 0
            node = node.children[ch]
        return node.cnt

    def countWordsStartingWith(self, prefix: str) -> int:
        """
        Interview explanation:
        Return number of inserted words with given prefix.

        Algorithm:
        - Walk prefix; return node.pref.

        Complexity: O(L).
        """
        node = self
        for ch in prefix:
            if ch not in node.children:
                return 0
            node = node.children[ch]
        return node.pref

    def erase(self, word: str) -> None:
        """
        Interview explanation:
        Remove one occurrence of word (guaranteed present). Decrement pref/cnt.

        Algorithm:
        - Walk word; each node.pref -= 1; terminal.cnt -= 1.

        Complexity: O(L).
        """
        node = self
        for ch in word:
            node = node.children[ch]
            node.pref -= 1
        node.cnt -= 1
# @lc code=end
