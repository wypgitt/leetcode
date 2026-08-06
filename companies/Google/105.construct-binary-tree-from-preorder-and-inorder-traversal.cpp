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
    TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
        /*
        Approach:
        preorder[preL] is the root. Its index in inorder splits left and right
        subtrees, and the left subtree size determines the preorder ranges. An
        unordered_map gives O(1) root index lookup.

        Complexity: O(n) time and O(n) space.
        */
        unordered_map<int, int> index;
        for (int i = 0; i < (int)inorder.size(); ++i) index[inorder[i]] = i;
        function<TreeNode*(int, int, int, int)> build = [&](int preL, int preR, int inL, int inR) -> TreeNode* {
            if (preL > preR) return nullptr;
            int rootVal = preorder[preL];
            int mid = index[rootVal];
            int leftSize = mid - inL;
            TreeNode* root = new TreeNode(rootVal);
            root->left = build(preL + 1, preL + leftSize, inL, mid - 1);
            root->right = build(preL + leftSize + 1, preR, mid + 1, inR);
            return root;
        };
        return build(0, (int)preorder.size() - 1, 0, (int)inorder.size() - 1);
    }
};
