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

// Definition for singly-linked list.
// struct ListNode {
//     int val;
//     ListNode *next;
//     ListNode() : val(0), next(nullptr) {}
//     ListNode(int x) : val(x), next(nullptr) {}
//     ListNode(int x, ListNode *next) : val(x), next(next) {}
// };


class Solution {
public:
    ListNode* rotateRight(ListNode* head, int k) {
        /*
        Approach:
        Count the list length and connect the tail to the head to form a cycle.
        The new tail is length - (k % length) - 1 steps from the old head. Break
        the cycle after that node.

        Complexity: O(n) time and O(1) space.
        */
        if (!head || !head->next || k == 0) return head;
        int length = 1;
        ListNode* tail = head;
        while (tail->next) {
            tail = tail->next;
            ++length;
        }
        k %= length;
        if (k == 0) return head;
        tail->next = head;
        int steps = length - k - 1;
        ListNode* newTail = head;
        while (steps--) newTail = newTail->next;
        ListNode* newHead = newTail->next;
        newTail->next = nullptr;
        return newHead;
    }
};
