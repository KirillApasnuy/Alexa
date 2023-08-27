import pickle
def doAnswer(voice):
    print(voice)
    with open('../answer.pickle', 'wb') as file:
        pickle.dump(voice, file)
    return True