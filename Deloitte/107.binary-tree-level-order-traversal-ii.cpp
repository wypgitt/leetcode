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
    vector<vector<int>> levelOrderBottom(TreeNode* root) {
        /*
        Approach:
        Perform standard BFS to collect levels top to bottom, then reverse the
        list of levels at the end.

        Complexity: O(n) time and O(w) queue space excluding output.
        */
        if (!root) return {};
        vector<vector<int>> levels;
        queue<TreeNode*> q;
        q.push(root);
        while (!q.empty()) {
            int size = (int)q.size();
            vector<int> level;
            for (int i = 0; i < size; ++i) {
                TreeNode* node = q.front();
                q.pop();
                level.push_back(node->val);
                if (node->left) q.push(node->left);
                if (node->right) q.push(node->right);
            }
            levels.push_back(move(level));
        }
        reverse(levels.begin(), levels.end());
        return levels;
    }
};
