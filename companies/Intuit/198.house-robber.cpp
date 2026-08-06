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


class Solution {
public:
    int rob(vector<int>& nums) {
        /*
        Approach: dynamic programming with two rolling values. prev1 is the best
        amount through the previous house; prev2 is the best through the house
        before that. For each house, choose skip or rob.

        Complexity: O(n) time, O(1) space.
        */
        int prev2 = 0, prev1 = 0;
        for (int num : nums) {
            int cur = max(prev1, prev2 + num);
            prev2 = prev1;
            prev1 = cur;
        }
        return prev1;
    }
};
