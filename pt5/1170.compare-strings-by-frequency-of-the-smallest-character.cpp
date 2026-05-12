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
    vector<int> numSmallerByFrequency(vector<string>& queries, vector<string>& words) {
        vector<int> wordFreq;
        for (const string& word : words) wordFreq.push_back(freq(word));
        sort(wordFreq.begin(), wordFreq.end());

        vector<int> answer;
        for (const string& query : queries) {
            int f = freq(query);
            auto it = upper_bound(wordFreq.begin(), wordFreq.end(), f);
            answer.push_back(wordFreq.end() - it);
        }
        return answer;
    }

private:
    int freq(const string& s) {
        char smallest = 'z';
        int count = 0;
        for (char ch : s) {
            if (ch < smallest) {
                smallest = ch;
                count = 1;
            } else if (ch == smallest) {
                ++count;
            }
        }
        return count;
    }
};

/*
Interview Explanation

Core idea:
For each query, count how many word frequencies are strictly greater than the
query frequency. Sorting word frequencies enables binary search.

C++ data structures:
- vector<int> wordFreq stores f(word) for all words.
- upper_bound finds the first frequency greater than f(query).

Algorithm:
1. Compute and sort word frequencies.
2. For each query, compute f(query).
3. Use upper_bound to count sorted values greater than it.

Correctness:
upper_bound returns the first element > f(query). Every element from that
position to the end is a word with strictly greater frequency, exactly the
required count.

Complexity:
Let W be word count and Q query count. Sorting is O(W log W). Each query costs
O(length + log W). Space is O(W).

Edge cases:
- Equal frequencies are not counted because upper_bound skips them.
- Strings with all same letters are handled by freq.
*/
