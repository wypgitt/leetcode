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
    int maxRepOpt1(string text) {
        vector<int> total(26, 0);
        for (char ch : text) ++total[ch - 'a'];

        int answer = 0;
        for (int ch = 0; ch < 26; ++ch) {
            int left = 0;
            int other = 0;
            for (int right = 0; right < (int)text.size(); ++right) {
                if (text[right] - 'a' != ch) ++other;
                while (other > 1) {
                    if (text[left] - 'a' != ch) --other;
                    ++left;
                }
                answer = max(answer, min(total[ch], right - left + 1));
            }
        }

        return answer;
    }
};

/*
Interview Explanation

Core idea:
For each target character, find the longest window containing at most one other
character. That one other character can be swapped out if another target
character exists elsewhere.

C++ data structures:
- vector<int> total counts total occurrences of each character.
- Sliding-window pointers scan for each target character.

Algorithm:
For each character c, maintain a window with at most one non-c character.
The candidate length is window size capped by total[c], because we cannot
create more copies of c than exist in the string.

Correctness:
After at most one swap, a repeated-character substring can contain at most one
wrong character before the swap. The sliding window enumerates the longest such
window for each character. Capping by total count handles whether an outside
character is available to swap in.

Complexity:
O(26n) time, O(1) space.

Edge cases:
- All characters equal returns n.
- Single character string returns 1.
- If no outside copy exists, the total-count cap prevents overcounting.
*/
