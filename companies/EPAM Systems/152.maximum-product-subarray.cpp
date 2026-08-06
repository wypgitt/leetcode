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
    int maxProduct(vector<int>& nums) {
        /*
        Approach: keep both maximum and minimum product ending at the current
        index. A negative number can turn the minimum into the maximum, so swap
        the two running values before updating when num is negative.

        Complexity: O(n) time, O(1) space.
        */
        int curMax = nums[0], curMin = nums[0], ans = nums[0];
        for (int i = 1; i < (int)nums.size(); ++i) {
            int num = nums[i];
            if (num < 0) swap(curMax, curMin);
            curMax = max(num, curMax * num);
            curMin = min(num, curMin * num);
            ans = max(ans, curMax);
        }
        return ans;
    }
};
