package main

import "sort"

func numSmallerByFrequency(queries []string, words []string) []int {
	frequency := func(word string) int {
		smallest := byte('z')
		count := 0
		for i := 0; i < len(word); i++ {
			if word[i] < smallest {
				smallest = word[i]
				count = 1
			} else if word[i] == smallest {
				count++
			}
		}
		return count
	}

	wordFrequencies := make([]int, len(words))
	for i, word := range words {
		wordFrequencies[i] = frequency(word)
	}
	sort.Ints(wordFrequencies)

	answer := make([]int, len(queries))
	for i, query := range queries {
		queryFrequency := frequency(query)
		firstGreater := sort.Search(len(wordFrequencies), func(j int) bool {
			return wordFrequencies[j] > queryFrequency
		})
		answer[i] = len(wordFrequencies) - firstGreater
	}
	return answer
}

