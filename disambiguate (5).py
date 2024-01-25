
from nltk.corpus import wordnet as wn

def disambiguateTerms(terms):
	for t_i in terms:    # t_i is target term
		selSense = None
		selScore = 0.0
#        print(wn.synsets(t_i,wn.NOUN))
		for s_ti in wn.synsets(t_i, lang='ita', pos=wn.NOUN):
			score_i = 0.0
			for t_j in terms:    # t_j term in t_i's context window
				if (t_i==t_j):
					continue
				bestScore = 0.0
				for s_tj in wn.synsets(t_j, lang='ita', pos=wn.NOUN):
					tempScore = s_ti.wup_similarity(s_tj)
					if (tempScore>bestScore):
						bestScore=tempScore
				score_i = score_i + bestScore
			if (score_i>selScore):
				selScore = score_i
				selSense = s_ti
		if (selSense is not None):
			print(t_i,": ",selSense,", ",selSense.definition())
			print(selSense.lemmas('ita'))
			print("Score: ",selScore)
		else:
			print(t_i,": --")

input_terms = input("Inserisci le tre parole separate da uno spazio: ").split()

disambiguateTerms(input_terms)
