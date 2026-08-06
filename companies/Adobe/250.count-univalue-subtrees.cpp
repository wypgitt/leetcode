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
    int countUnivalSubtrees(TreeNode* root) {
        /*
        Approach: postorder DFS. An empty subtree is univalue. A node's subtree
        is univalue if both child subtrees are univalue and any existing child has
        the same value as the node. Count every subtree that passes this test.

        Complexity: O(n) time, O(h) recursion space.
        */
        int count = 0;
        function<bool(TreeNode*)> dfs = [&](TreeNode* node) -> bool {
            if (!node) return true;
            bool leftOk = dfs(node->left);
            bool rightOk = dfs(node->right);
            if (!leftOk || !rightOk) return false;
            if (node->left && node->left->val != node->val) return false;
            if (node->right && node->right->val != node->val) return false;
            ++count;
            return true;
        };
        dfs(root);
        return count;
    }
};
