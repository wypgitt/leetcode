#include <algorithm>
#include <array>
#include <climits>
#include <cmath>
#include <condition_variable>
#include <cstdlib>
#include <deque>
#include <functional>
#include <map>
#include <mutex>
#include <numeric>
#include <queue>
#include <set>
#include <sstream>
#include <stack>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

// LeetCode provides ListNode.
// struct ListNode {
//     int val;
//     ListNode *next;
//     ListNode() : val(0), next(nullptr) {}
//     ListNode(int x) : val(x), next(nullptr) {}
//     ListNode(int x, ListNode *next) : val(x), next(next) {}
// };

class Solution {
public:
    ListNode* removeZeroSumSublists(ListNode* head) {
        ListNode dummy(0);
        dummy.next = head;

        unordered_map<int, ListNode*> last;
        int prefix = 0;
        for (ListNode* node = &dummy; node; node = node->next) {
            prefix += node->val;
            last[prefix] = node;
        }

        prefix = 0;
        for (ListNode* node = &dummy; node; node = node->next) {
            prefix += node->val;
            node->next = last[prefix]->next;
        }

        return dummy.next;
    }
};

/*
Interview Explanation

Core idea:
If two prefix sums are equal, the nodes between them sum to zero. Keeping the
last occurrence of each prefix sum removes the widest zero-sum span.

C++ data structures:
- Dummy ListNode handles removals at the head.
- unordered_map<int, ListNode*> maps prefix sum to its last node.

Algorithm:
1. First pass: compute prefix sums and store the last node for each sum.
2. Second pass: recompute prefix sums and jump node->next to last[prefix]->next.
3. Return dummy.next.

Correctness:
Equal prefix sums around a segment mean that segment sums to zero. Jumping to
the node after the last equal prefix removes all zero-sum nodes between. Doing
this for every prefix eliminates all zero-sum consecutive segments.

Complexity:
O(n) average time and O(n) space.

Edge cases:
- A zero-sum prefix is removed by the dummy prefix sum 0.
- Multiple overlapping zero-sum ranges are handled by last occurrence jumps.
*/
