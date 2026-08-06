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
    bool isValidBST(TreeNode* root) {
        /*
        Approach:
        Each node must satisfy exclusive bounds inherited from all ancestors,
        not just its parent. Recurse left with a tighter upper bound and right
        with a tighter lower bound.

        C++ notes:
        long long bounds safely sit outside the int node value range.

        Complexity: O(n) time and O(h) recursion space.
        */
        function<bool(TreeNode*, long long, long long)> dfs = [&](TreeNode* node, long long low, long long high) {
            if (!node) return true;
            if (!(low < node->val && node->val < high)) return false;
            return dfs(node->left, low, node->val) && dfs(node->right, node->val, high);
        };
        return dfs(root, LLONG_MIN, LLONG_MAX);
    }
};
