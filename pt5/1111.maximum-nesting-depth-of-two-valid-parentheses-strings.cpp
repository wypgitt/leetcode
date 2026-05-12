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

class Solution {
public:
    vector<int> maxDepthAfterSplit(string seq) {
        vector<int> answer;
        answer.reserve(seq.size());
        int depth = 0;

        for (char ch : seq) {
            if (ch == '(') {
                ++depth;
                answer.push_back(depth % 2);
            } else {
                answer.push_back(depth % 2);
                --depth;
            }
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
To minimize the maximum nesting depth between two valid subsequences, split
parentheses by depth parity. Adjacent levels alternate between group 0 and 1.

C++ data structures:
- vector<int> stores the group assignment for each character.
- A single depth counter tracks current nesting level.

Algorithm:
1. For '(', increment depth first, then assign depth parity.
2. For ')', assign current depth parity, then decrement.
3. Matching parentheses get the same parity because they are at the same depth.

Correctness:
Every matching pair is assigned to the same group, so both groups remain valid
parentheses strings. Since depths alternate by parity, no group receives two
consecutive nesting levels, which keeps each group's maximum depth as balanced
as possible.

Complexity:
O(n) time and O(n) output space.

Edge cases:
- Empty string would produce empty output.
- Depth 1 alternates consistently.
- Deep nesting is split roughly in half.
*/
