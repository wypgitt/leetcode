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
    ListNode* detectCycle(ListNode* head) {
        /*
        Approach: Floyd's slow/fast pointers detect a meeting point inside a
        cycle. Then move one pointer from head and one from the meeting point;
        their next meeting point is the cycle entry.

        Complexity: O(n) time, O(1) space.
        */
        ListNode* slow = head;
        ListNode* fast = head;
        while (fast && fast->next) {
            slow = slow->next;
            fast = fast->next->next;
            if (slow == fast) {
                ListNode* finder = head;
                while (finder != slow) {
                    finder = finder->next;
                    slow = slow->next;
                }
                return finder;
            }
        }
        return nullptr;
    }
};
