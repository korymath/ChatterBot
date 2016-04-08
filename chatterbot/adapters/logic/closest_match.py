from chatterbot.adapters.exceptions import EmptyDatasetException
from .base_match import BaseMatchAdapter
from fuzzywuzzy import process
from tqdm import tqdm
import time
from multiprocessing import Pool

from fuzzywuzzy import fuzz
import Levenshtein
import operator
import pickle

from collections import Counter

class ClosestMatchAdapter(BaseMatchAdapter):
    def compareStrings(self, strings):
        leven1 = fuzz.token_set_ratio(strings[0],strings[1])
        leven2 = Levenshtein.ratio(str(strings[0]),str(strings[1]))
        return (strings[0],strings[1],leven1+leven2*100,leven2)

    def searchThroughList(self, searchString, listOfStrings):
        if len(listOfStrings)==0:
            return "You need to save a hash to defaultHash.p if you want to load one automatically!"
        
        stringList = []
        for string in listOfStrings:
            stringList.append((searchString.lower(),string.lower()))
            
        # pool2 = Pool(2)
        # results = pool2.map(self.compareStrings, stringList)
        # pool2.close()
        # pool2.join()

        results = []
        for s_l in stringList:
            results.append(self.compareStrings(s_l))

        #print (sorted(results, key=operator.itemgetter(2, 3), reverse=True))[:10]
        topResult = (sorted(results, key=operator.itemgetter(2, 3), reverse=True))[0]
        return listOfStrings[[x.lower() for x in listOfStrings].index(topResult[1])]

    def searchThroughHash(self,searchString,sHash):
        if len(sHash)==0:
            return "You need to save a hash to defaultHash.p if you want to load one automatically!"
        searchString = searchString.lower()
        possibleStrings = []
        for i in range(0,len(searchString)-2):
            doublet = searchString[i:i+3]
            if doublet in sHash:
                possibleStrings += sHash[doublet]
        c = Counter(possibleStrings)
        mostPossible = []
        for p in c.most_common(1000):
            mostPossible.append(p[0])
        return self.searchThroughList(searchString,mostPossible)

    def generateSearchableHashFromList(self, listOfStrings):
        sHash = {}
        for string in tqdm(listOfStrings):
            for i in range(0,len(string)-2):
                doublet = string[i:i+3].lower()
                if doublet not in sHash:
                    sHash[doublet] = []
                sHash[doublet].append(string)
        return sHash

    def get(self, input_statement, hash_list, statement_list=None):
        """
        Takes a statement string and a list of statement strings.
        Returns the closest matching statement from the list.
        """
        statement_list = self.get_available_statements(statement_list)

        if not statement_list:
            if self.has_storage_context:
                # Use a randomly picked statement
                return hash_list, 0, self.context.storage.get_random()
            else:
                raise EmptyDatasetException

        # Get the text of each statement
        text_of_all_statements = []
        for statement in statement_list:
            text_of_all_statements.append(statement.text)

        # Check if an exact match exists
        if input_statement.text in text_of_all_statements:
            return hash_list, 1, input_statement

        # closest_match, confidence = process.extract(input_statement.text,text_of_all_statements,limit=1)[0]
        confidence = 100
        
        if hash_list is None:
            hash_list = self.generateSearchableHashFromList(text_of_all_statements)
        
        closest_match = self.searchThroughHash(input_statement.text, hash_list)
        
        # Convert the confidence integer to a percent
        confidence /= 100.0

        return hash_list, confidence, next((s for s in statement_list if s.text == closest_match), None)
