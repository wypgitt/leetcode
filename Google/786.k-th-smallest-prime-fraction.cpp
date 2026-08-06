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
    vector<int> kthSmallestPrimeFraction(vector<int>& arr, int k) {
        using State = tuple<double, int, int>;
        priority_queue<State, vector<State>, greater<State>> pq;
        int n = arr.size();
        for (int j = 1; j < n; ++j) pq.push({(double)arr[0] / arr[j], 0, j});
        while (--k) {
            auto [value, i, j] = pq.top(); pq.pop();
            if (i + 1 < j) pq.push({(double)arr[i + 1] / arr[j], i + 1, j});
        }
        auto [value, i, j] = pq.top();
        return {arr[i], arr[j]};
    }
};

/*
Interview explanation:
For each denominator, fractions with increasing numerator index are sorted. A min-heap merges these sorted lists until the kth fraction is at the top.

C++ data structures: priority_queue with greater<tuple<...>> acts as a min-heap. Tuple stores fraction value and indices.

Edge cases: only numerator indices less than denominator index are pushed.

Complexity: O((n+k) log n) time and O(n) space.
*/
