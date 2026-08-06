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

// Definition for a Node.
// class Node {
// public:
//     int val;
//     Node* left;
//     Node* right;
//     Node* next;
//     Node() : val(0), left(nullptr), right(nullptr), next(nullptr) {}
//     Node(int _val) : val(_val), left(nullptr), right(nullptr), next(nullptr) {}
//     Node(int _val, Node* _left, Node* _right, Node* _next)
//         : val(_val), left(_left), right(_right), next(_next) {}
// };


class Solution {
public:
    Node* connect(Node* root) {
        /*
        Approach:
        The tree is perfect, so every internal node has both children. Walk each
        level using existing next pointers. Link node->left to node->right, and
        node->right to node->next->left when a neighbor exists.

        C++ notes:
        Node* next pointers are mutated in place; no queue is needed.

        Complexity: O(n) time and O(1) extra space.
        */
        Node* leftmost = root;
        while (leftmost && leftmost->left) {
            Node* node = leftmost;
            while (node) {
                node->left->next = node->right;
                if (node->next) node->right->next = node->next->left;
                node = node->next;
            }
            leftmost = leftmost->left;
        }
        return root;
    }
};
