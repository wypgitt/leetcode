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
    vector<string> beforeAndAfterPuzzles(vector<string>& phrases) {
        set<string> results;
        int n = phrases.size();

        vector<string> first(n), last(n);
        for (int i = 0; i < n; ++i) {
            first[i] = firstWord(phrases[i]);
            last[i] = lastWord(phrases[i]);
        }

        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (i == j || last[i] != first[j]) continue;
                results.insert(phrases[i] + phrases[j].substr(first[j].size()));
            }
        }

        return vector<string>(results.begin(), results.end());
    }

private:
    string firstWord(const string& phrase) {
        int pos = phrase.find(' ');
        return pos == (int)string::npos ? phrase : phrase.substr(0, pos);
    }

    string lastWord(const string& phrase) {
        int pos = phrase.find_last_of(' ');
        return pos == (int)string::npos ? phrase : phrase.substr(pos + 1);
    }
};

/*
Interview Explanation

Core idea:
Phrase A can be followed by phrase B if A's last word equals B's first word.
The shared word appears once in the merged result.

C++ data structures:
- vector<string> caches first and last words.
- set<string> deduplicates answers and keeps them sorted lexicographically.

Algorithm:
1. Precompute first and last word for each phrase.
2. Try every ordered pair i != j.
3. If last[i] == first[j], append phrase j after removing its first word.
4. Return sorted unique results from the set.

Correctness:
Every valid before-and-after puzzle is an ordered pair of distinct phrases with
matching boundary words, so the nested loops generate all valid puzzles. The
substring removes the duplicated boundary word exactly once. The set enforces
unique sorted output.

Complexity:
O(n^2 * L) time for phrase concatenation/comparison and O(a * L) space for
answers.

Edge cases:
- Single-word phrases work as both first and last word.
- Duplicate generated strings appear once.
*/
