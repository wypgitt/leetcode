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


class Trie {
    struct TrieNode {
        unordered_map<char, TrieNode*> child;
        bool isWord = false;
    };
    TrieNode* root;

public:
    Trie() {
        /*
        Approach: trie/prefix tree. Each edge is a character; search walks the
        word and succeeds only if the final node is marked as a full word.
        startsWith only requires the prefix path to exist.

        C++ notes: unordered_map<char, TrieNode*> mirrors Python nested dicts and
        supports sparse child sets.
        Complexity: insert/search/startsWith are O(L) time, O(total characters)
        space over all inserted words.
        */
        root = new TrieNode();
    }

    void insert(string word) {
        TrieNode* node = root;
        for (char ch : word) {
            if (!node->child.count(ch)) node->child[ch] = new TrieNode();
            node = node->child[ch];
        }
        node->isWord = true;
    }

    bool search(string word) {
        TrieNode* node = root;
        for (char ch : word) {
            if (!node->child.count(ch)) return false;
            node = node->child[ch];
        }
        return node->isWord;
    }

    bool startsWith(string prefix) {
        TrieNode* node = root;
        for (char ch : prefix) {
            if (!node->child.count(ch)) return false;
            node = node->child[ch];
        }
        return true;
    }
};
