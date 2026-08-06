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
        The tree is not perfect, so build the next level while walking the
        current level through already-established next pointers. A dummy head and
        tail pointer append each existing child without using a queue.

        C++ notes:
        The dummy Node is stack allocated; only its next pointer is used as the
        head of the next level.

        Complexity: O(n) time and O(1) extra space.
        */
        Node* current = root;
        while (current) {
            Node dummy(0);
            Node* tail = &dummy;
            while (current) {
                if (current->left) {
                    tail->next = current->left;
                    tail = tail->next;
                }
                if (current->right) {
                    tail->next = current->right;
                    tail = tail->next;
                }
                current = current->next;
            }
            current = dummy.next;
        }
        return root;
    }
};
