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
    int numFactoredBinaryTrees(vector<int>& arr) {
        const long long MOD = 1000000007;
        sort(arr.begin(), arr.end());
        unordered_set<int> values(arr.begin(), arr.end());
        unordered_map<int, long long> dp;
        for (int x : arr) {
            long long total = 1;
            for (int a : arr) {
                if (1LL * a * a > x) break;
                if (x % a == 0 && values.count(x / a)) {
                    int b = x / a;
                    long long ways = dp[a] * dp[b] % MOD;
                    total = (total + (a == b ? ways : 2 * ways)) % MOD;
                }
            }
            dp[x] = total;
        }
        long long ans = 0;
        for (auto& [x, ways] : dp) ans = (ans + ways) % MOD;
        return ans;
    }
};

/*
Interview explanation:
Sort values so factor roots are computed before products. For each root x, every factor pair a*b=x combines any left tree rooted at a with any right tree rooted at b.

C++ data structures: unordered_map<int,long long> stores DP counts by root value; unordered_set<int> tests factor existence.

Edge cases: every value contributes a single-node tree. Unequal factor pairs are doubled for left/right order.

Complexity: O(n^2) time in the worst case and O(n) space.
*/
