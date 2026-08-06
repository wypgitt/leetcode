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
    int minSubArrayLen(int target, vector<int>& nums) {
        /*
        Approach: positive numbers allow a sliding window. Expand right to grow
        the sum; while sum is at least target, update the answer and shrink left
        to find a shorter valid window.

        Complexity: O(n) time, O(1) space.
        */
        int left = 0, total = 0, best = nums.size() + 1;
        for (int right = 0; right < (int)nums.size(); ++right) {
            total += nums[right];
            while (total >= target) {
                best = min(best, right - left + 1);
                total -= nums[left++];
            }
        }
        return best == (int)nums.size() + 1 ? 0 : best;
    }
};
