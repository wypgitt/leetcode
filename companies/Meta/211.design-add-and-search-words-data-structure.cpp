#include <algorithm>
#include <array>
#include <cctype>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;


class WordDictionary {
    struct TrieNode {
        unordered_map<char, TrieNode*> child;
        bool isWord = false;
    };
    TrieNode* root;

public:
    WordDictionary() {
        /*
        Approach: trie for inserted words. Literal search follows one child. A
        '.' wildcard recursively tries every non-null child at that position.

        C++ notes: unordered_map<char, TrieNode*> implements the sparse child map
        used by Python dicts.
        Complexity: addWord O(L). search is O(L) for literal words and up to
        O(branches^wildcards) with '.', bounded by trie size.
        */
        root = new TrieNode();
    }

    void addWord(string word) {
        TrieNode* node = root;
        for (char ch : word) {
            if (!node->child.count(ch)) node->child[ch] = new TrieNode();
            node = node->child[ch];
        }
        node->isWord = true;
    }

    bool search(string word) {
        function<bool(int, TrieNode*)> dfs = [&](int i, TrieNode* node) -> bool {
            if (i == (int)word.size()) return node->isWord;
            char ch = word[i];
            if (ch == '.') {
                for (auto& [key, child] : node->child) {
                    if (dfs(i + 1, child)) return true;
                }
                return false;
            }
            return node->child.count(ch) && dfs(i + 1, node->child[ch]);
        };
        return dfs(0, root);
    }
};
