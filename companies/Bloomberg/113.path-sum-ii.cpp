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
    vector<vector<int>> pathSum(TreeNode* root, int targetSum) {
        /*
        Approach:
        Backtrack root-to-leaf paths. path stores the current route and remain
        tracks the sum still needed. At a leaf, the path is valid exactly when
        remain equals the leaf value after subtraction.

        Complexity: O(n*h) worst-case for copying valid paths, O(h) stack.
        */
        vector<vector<int>> ans;
        vector<int> path;
        function<void(TreeNode*, int)> dfs = [&](TreeNode* node, int remain) {
            if (!node) return;
            path.push_back(node->val);
            remain -= node->val;
            if (!node->left && !node->right && remain == 0) ans.push_back(path);
            else {
                dfs(node->left, remain);
                dfs(node->right, remain);
            }
            path.pop_back();
        };
        dfs(root, targetSum);
        return ans;
    }
};
