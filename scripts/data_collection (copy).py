import timer

tim = timer.Timer("mouthed",1,"Mouthed_NewVocab_6_set4_take2.txt")

#word_list = ['yes', 'no']

word_list = [
"zero",
"one",
"two",
"three",
"four",
"five",
"six",
"seven",
"eight",
"nine",
"up",
"down",
"left",
"right"
]



word_list = word_list * 5
tim.run(word_list)

tim.mainloop()