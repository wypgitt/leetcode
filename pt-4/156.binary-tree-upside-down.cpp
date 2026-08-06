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
    TreeNode* upsideDownBinaryTree(TreeNode* root) {
        /*
        Approach: iteratively rotate the left spine. The old parent becomes the
        new right child, and the old right sibling becomes the new left child.
        Track parent and parentRight while moving down original left pointers.

        Complexity: O(h) time where h is left-spine length, O(1) space.
        */
        TreeNode* parent = nullptr;
        TreeNode* parentRight = nullptr;
        TreeNode* cur = root;
        while (cur) {
            TreeNode* nextLeft = cur->left;
            cur->left = parentRight;
            parentRight = cur->right;
            cur->right = parent;
            parent = cur;
            cur = nextLeft;
        }
        return parent;
    }
};
