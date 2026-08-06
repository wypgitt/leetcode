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
    TreeNode* buildTree(vector<int>& inorder, vector<int>& postorder) {
        /*
        Approach:
        postorder[postR] is the root. Its inorder index splits left and right
        subtrees. leftSize determines how to partition the postorder range.

        Complexity: O(n) time and O(n) space.
        */
        unordered_map<int, int> index;
        for (int i = 0; i < (int)inorder.size(); ++i) index[inorder[i]] = i;
        function<TreeNode*(int, int, int, int)> build = [&](int inL, int inR, int postL, int postR) -> TreeNode* {
            if (inL > inR) return nullptr;
            int rootVal = postorder[postR];
            int mid = index[rootVal];
            int leftSize = mid - inL;
            TreeNode* root = new TreeNode(rootVal);
            root->left = build(inL, mid - 1, postL, postL + leftSize - 1);
            root->right = build(mid + 1, inR, postL + leftSize, postR - 1);
            return root;
        };
        return build(0, (int)inorder.size() - 1, 0, (int)postorder.size() - 1);
    }
};
