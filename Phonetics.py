import pandas as pd
import textgrid, numpy, os

stressed_vowels_all_results = []
final_vowels_all_results = []
not_final_vowels_all_results = []

def textgrid_experiment(gridfile):
	
	global stressed_vowels_all_results,final_vowels_all_results,not_final_vowels_all_results
	
	# преобразуем textgrid в csv
	tgrid = textgrid.read_textgrid(gridfile)
	csv = pd.DataFrame(tgrid)

	# работаем со словами и находим количество звуков, длины слов и абсолютные длительности слов
	word_df = csv.loc[csv['tier'] == 'Word'][csv['name']!='']
	startpoints = word_df['start'].to_list()
	stoppoints = word_df['stop'].to_list()
	sound_df = csv.loc[csv['tier'] == 'Sound'][csv['name']!='']
	
	## ищу индексы тех звуков, начальные метки которых совпадают с начальными метками соответствующих слов
	start_indexes = []
	for startpoint in startpoints:
		start_indexes.append(sound_df.index[sound_df.start == startpoint].to_list())
	## ищу индексы тех звуков, конечные метки которых совпадают с конечными метками соответствующих слов
	stop_indexes = []
	for stoppoint in stoppoints:
		stop_indexes.append(sound_df.index[sound_df.stop == stoppoint].to_list())
		
	wordpoints = [] ###индексы начального и конечного звуков для каждого слова
	wrong_indexes = []
	for start,stop in zip(start_indexes,stop_indexes):
		if len(start) != 0 and len(stop) != 0:
			pair = start[0],stop[0]
			wordpoints.append(pair)
		else:
			for i,j in enumerate(start_indexes):
				if j == start:
					wrong_indexes.append(i) ###нахожу то, что не совпало
	wrong_indexes=set(wrong_indexes)				
	startpoints = [i for i in startpoints if startpoints.index(i) not in wrong_indexes] # убираю то, что не совпало
	stoppoints = [i for i in stoppoints if stoppoints.index(i) not in wrong_indexes] # убираю то, что не совпало
	
	absolute_durations = [] ###абсолютные длительности слов
	for start,stop in zip (startpoints,stoppoints):
		absolute_duration = stop-start
		absolute_durations.append(absolute_duration)
		
	amount_of_sounds_in_a_word = [] ###количество звуков в слове                                                     
	for two_points in wordpoints:	
		length = two_points[1]-two_points[0]+1
		amount_of_sounds_in_a_word.append(length)
			
	# находим отдельные звуки
	all_sounds = sound_df['name'].to_list()
	all_indexes = sound_df.index.to_list()

	## ударные
	stressed_indexes = []
	for a,b in zip(all_sounds,all_indexes):
		if "ˈ" in a: ###нахожу ударные по символу
			stressed_indexes.append(b)
	## безударные в конце слова
	vowels_end_word = []
	non_stressed_list2 = ['ь','ъ','ɑ'] #список
	for a,b in zip(all_sounds,all_indexes):
		if a in non_stressed_list2:
			if sound_df['stop'][b] in stoppoints: ###безударные в конце слова нахожу по метке конца слова
				vowels_end_word.append(b)

	## безударные не в конце слова
	non_stressed_non_end_word_indexes = []
	non_stressed_list1 = ['ʌ','ь','ъ','и','у','ы'] ###список
	for a,b in zip(all_sounds,all_indexes):
		if a in non_stressed_list1:
			if sound_df['stop'][b] not in stoppoints: ###безударные не в конце слова нахожу по несоответствию метке конца слова
				non_stressed_non_end_word_indexes.append(b)

	# находим относительную длительность звука
	stressed_v = []
	fin_v = []
	n_fin_v = []

	def result(kind_of_sound,result_list):
		for s_vowel in kind_of_sound:
			for word_marker in wordpoints:
				if s_vowel >= word_marker[0] and s_vowel <= word_marker[1]:
					true_word_index = wordpoints.index(word_marker)
					absolute_sound_duration = sound_df['stop'][s_vowel] - sound_df['start'][s_vowel] ###абсолютная длительность звука
					relative_duration = absolute_sound_duration*amount_of_sounds_in_a_word[true_word_index]/absolute_durations[true_word_index]
					result_list.append(relative_duration)
					
	## для ударных
	result(stressed_indexes,stressed_v)
	result_1 = numpy.mean(stressed_v)
	stressed_vowels_all_results.append(result_1)
	
	## для безударных в конце слова
	result(vowels_end_word,fin_v)
	result_2 = numpy.mean(fin_v)
	final_vowels_all_results.append(result_2)
	
	## для безударных не в конце слова
	result(non_stressed_non_end_word_indexes,n_fin_v)
	result_3 = numpy.mean(n_fin_v)
	not_final_vowels_all_results.append(result_3)

os.chdir("/home/daniil/Загрузки/Split/")
for f in os.listdir("/home/daniil/Загрузки/Split/"):
    if f.endswith(".TextGrid"):
        f2= os.path.abspath(f)
        textgrid_experiment(f2)

table = {"Ударные": stressed_vowels_all_results, "Безударные(конец_слова)": final_vowels_all_results,"Безударные(не_конец_слова)" : not_final_vowels_all_results}
df = pd.DataFrame(data=table)
