#include <algorithm>
#include <array>
#include <cmath>
#include <climits>
#include <cstdlib>
#include <functional>
#include <numeric>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
using namespace std;

class Solution {
public:
    string optimalDivision(vector<int>& nums) {
        if (nums.size() == 1) return to_string(nums[0]);
        if (nums.size() == 2) return to_string(nums[0]) + "/" + to_string(nums[1]);
        string ans = to_string(nums[0]) + "/(" + to_string(nums[1]);
        for (int i = 2; i < (int)nums.size(); ++i) ans += "/" + to_string(nums[i]);
        ans += ")";
        return ans;
    }
};

/*
Interview explanation:
To maximize the expression, minimize the denominator after nums[0]. Putting all remaining divisions inside one denominator moves nums[2..] into the numerator of the total value.

C++ data structures: string concatenation builds the required expression.

Edge cases: one or two numbers need no parentheses.

Complexity: O(n) time and output space.
*/
