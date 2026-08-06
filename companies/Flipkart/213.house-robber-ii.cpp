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
    int robLine(const vector<int>& nums, int left, int right) {
        int prev2 = 0, prev1 = 0;
        for (int i = left; i <= right; ++i) {
            int cur = max(prev1, prev2 + nums[i]);
            prev2 = prev1;
            prev1 = cur;
        }
        return prev1;
    }

public:
    int rob(vector<int>& nums) {
        /*
        Approach: houses form a circle, so first and last cannot both be robbed.
        Solve two linear robber problems: exclude last, and exclude first. The
        larger result is optimal.

        Complexity: O(n) time, O(1) space.
        */
        if (nums.size() == 1) return nums[0];
        return max(robLine(nums, 0, nums.size() - 2), robLine(nums, 1, nums.size() - 1));
    }
};
