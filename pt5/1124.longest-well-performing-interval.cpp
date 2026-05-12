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
    int longestWPI(vector<int>& hours) {
        unordered_map<int, int> firstSeen;
        int score = 0;
        int answer = 0;

        for (int i = 0; i < (int)hours.size(); ++i) {
            score += hours[i] > 8 ? 1 : -1;
            if (score > 0) {
                answer = i + 1;
            } else {
                if (!firstSeen.count(score)) firstSeen[score] = i;
                if (firstSeen.count(score - 1)) {
                    answer = max(answer, i - firstSeen[score - 1]);
                }
            }
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
Map tiring days to +1 and non-tiring days to -1. An interval is well-performing
when its sum is positive.

C++ data structures:
- unordered_map<int,int> stores the first index where each prefix score appears.
- Prefix score lets interval sums be computed by subtraction.

Algorithm:
1. Scan hours and update score.
2. If score > 0, the whole prefix is valid.
3. Otherwise, remember the first occurrence of score.
4. If score-1 appeared earlier, the interval after that index has positive sum.

Correctness:
For interval (j, i], sum = prefix[i] - prefix[j]. We need this to be positive,
so prefix[j] < prefix[i]. The closest guaranteed smaller score we need to
check is score-1 because scores change by one. Keeping earliest positions
maximizes interval length.

Complexity:
O(n) average time and O(n) space.

Edge cases:
- All tiring days returns n.
- No positive interval returns 0.
- Alternating days are handled by prefix scores.
*/
