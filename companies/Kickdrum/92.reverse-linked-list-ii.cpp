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
    ListNode* reverseBetween(ListNode* head, int left, int right) {
        /*
        Approach:
        Move prev to the node before the segment. Then use head insertion:
        repeatedly remove the node after cur and insert it directly after prev.
        This reverses only [left, right] without extra nodes.

        Complexity: O(n) time and O(1) space.
        */
        ListNode dummy(0, head);
        ListNode* prev = &dummy;
        for (int i = 0; i < left - 1; ++i) prev = prev->next;
        ListNode* cur = prev->next;
        for (int i = 0; i < right - left; ++i) {
            ListNode* move = cur->next;
            cur->next = move->next;
            move->next = prev->next;
            prev->next = move;
        }
        return dummy.next;
    }
};
