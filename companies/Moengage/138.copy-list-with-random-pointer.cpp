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

// Definition for a Node.
// class Node {
// public:
//     int val;
//     Node* next;
//     Node* random;
//     Node(int _val) : val(_val), next(nullptr), random(nullptr) {}
// };


class Solution {
public:
    Node* copyRandomList(Node* head) {
        /*
        Approach: interleave cloned nodes after their originals, wire clone
        random pointers by using original->random->next, then detach the cloned
        list while restoring the original list.

        C++ notes: this avoids unordered_map<Node*, Node*> and uses only raw
        next/random pointers supplied by LeetCode's Node type.
        Complexity: O(n) time, O(1) extra space excluding the new nodes.
        */
        if (!head) return nullptr;
        for (Node* cur = head; cur; cur = cur->next->next) {
            Node* copied = new Node(cur->val);
            copied->next = cur->next;
            cur->next = copied;
        }
        for (Node* cur = head; cur; cur = cur->next->next) {
            if (cur->random) cur->next->random = cur->random->next;
        }
        Node* copiedHead = head->next;
        Node* cur = head;
        while (cur) {
            Node* copied = cur->next;
            cur->next = copied->next;
            cur = cur->next;
            copied->next = cur ? cur->next : nullptr;
        }
        return copiedHead;
    }
};
