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
    int arrayNesting(vector<int>& nums) {
        int best = 0;
        for (int i = 0; i < (int)nums.size(); ++i) {
            if (nums[i] == -1) continue;
            int count = 0, j = i;
            while (nums[j] != -1) {
                int nxt = nums[j];
                nums[j] = -1;
                j = nxt;
                ++count;
            }
            best = max(best, count);
        }
        return best;
    }
};

/*
Interview explanation:
Because nums is a permutation, following indices forms disjoint cycles. Mark each visited index and keep the largest cycle length.

C++ data structures: vector<int> is mutated using -1 as a sentinel outside the valid range.

Edge cases: one-element cycles count as length 1.

Complexity: O(n) time and O(1) extra space.
*/
