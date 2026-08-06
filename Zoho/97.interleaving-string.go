package leetcode

// IsInterleave97 uses one-dimensional DP where dp[j] says whether s3[:i+j] can
// be formed from s1[:i] and s2[:j]. Each state can come from s1's last char or
// s2's last char.
//
// Time: O(m*n). Space: O(n).
func IsInterleave97(s1 string, s2 string, s3 string) bool {
	if len(s1)+len(s2) != len(s3) {
		return false
	}
	n := len(s2)
	dp := make([]bool, n+1)
	dp[0] = true
	for i := 0; i <= len(s1); i++ {
		for j := 0; j <= n; j++ {
			if i == 0 && j == 0 {
				continue
			}
			k := i + j - 1
			from1 := i > 0 && dp[j] && s1[i-1] == s3[k]
			from2 := j > 0 && dp[j-1] && s2[j-1] == s3[k]
			dp[j] = from1 || from2
		}
	}
	return dp[n]
}
