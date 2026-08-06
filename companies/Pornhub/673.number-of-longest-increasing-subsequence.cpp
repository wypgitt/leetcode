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
    int findNumberOfLIS(vector<int>& nums) {
        int n = nums.size();
        if (n == 0) return 0;
        vector<int> len(n, 1), cnt(n, 1);
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < i; ++j) {
                if (nums[j] < nums[i]) {
                    if (len[j] + 1 > len[i]) {
                        len[i] = len[j] + 1;
                        cnt[i] = cnt[j];
                    } else if (len[j] + 1 == len[i]) {
                        cnt[i] += cnt[j];
                    }
                }
            }
        }
        int longest = *max_element(len.begin(), len.end());
        int ans = 0;
        for (int i = 0; i < n; ++i) if (len[i] == longest) ans += cnt[i];
        return ans;
    }
};

/*
Interview explanation:
For each index, track the LIS length ending there and how many LIS of that length end there. Earlier smaller values can extend into the current index.

C++ data structures: two vector<int> arrays hold lengths and counts.

Edge cases: equal values cannot extend because the subsequence must be strictly increasing.

Complexity: O(n^2) time and O(n) space.
*/
