#include <algorithm>
#include <cctype>
#include <climits>
#include <cmath>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <sstream>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>
using namespace std;

// Definition for a binary tree node.
// struct TreeNode {
//     int val;
//     TreeNode *left;
//     TreeNode *right;
//     TreeNode() : val(0), left(nullptr), right(nullptr) {}
//     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
//     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
// };


class Solution {
public:
    vector<TreeNode*> generateTrees(int n) {
        /*
        Approach:
        For each root value, recursively generate every valid left subtree from
        smaller values and every valid right subtree from larger values, then
        combine each pair under a new root. Empty subtree is represented by a
        single nullptr option so leaf combinations work naturally.

        C++ notes:
        unordered_map<string, vector<TreeNode*>> memoizes subtree ranges similar
        to Python lru_cache. The returned subtrees may share cached child
        pointers, which matches the source algorithm and is fine for LeetCode's
        read-only validation.

        Complexity: O(C_n * n) time and space for Catalan number C_n trees.
        */
        unordered_map<string, vector<TreeNode*>> memo;
        function<vector<TreeNode*>(int, int)> build = [&](int lo, int hi) -> vector<TreeNode*> {
            if (lo > hi) return {nullptr};
            string key = to_string(lo) + "," + to_string(hi);
            if (memo.count(key)) return memo[key];
            vector<TreeNode*> trees;
            for (int rootVal = lo; rootVal <= hi; ++rootVal) {
                vector<TreeNode*> leftTrees = build(lo, rootVal - 1);
                vector<TreeNode*> rightTrees = build(rootVal + 1, hi);
                for (TreeNode* left : leftTrees) {
                    for (TreeNode* right : rightTrees) {
                        TreeNode* root = new TreeNode(rootVal);
                        root->left = left;
                        root->right = right;
                        trees.push_back(root);
                    }
                }
            }
            memo[key] = trees;
            return trees;
        };
        return build(1, n);
    }
};
