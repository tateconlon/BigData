# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 17:48:06 2018

@author: eccrawford
"""

import csv
import scrapy
from scrapy.selector import Selector

class PaperSpider(scrapy.Spider):
    name = 'Walters'
    pubmedIds = open("C:\\Users\\eccrawford\\Documents\\CISC 490\\citedPapers.csv", "rb")
    
    def generateStartURLs(pubmedData):
      urlsList = []
      pubmed = "https://www.ncbi.nlm.nih.gov/pubmed/"
      data = csv.reader(pubmedData, delimiter=",")
      
      papersDict = {row[0]: row[1:] for row in data}
      
      for key in papersDict:
        while '' in papersDict[key]:
          papersDict[key].remove('')
       
      retractedPapers = papersDict.keys()
      citedPapers = papersDict.values()
      
      for paper in retractedPapers:
        urlsList.append(pubmed+str(paper))
        
      for cited in citedPapers:
        for c in cited:
          urlsList.append(pubmed+str(c))
      return urlsList, papersDict
    
    start_urls, papers = generateStartURLs(pubmedIds)
    
#    for line in start_urls:
#      with open("urls.txt", "a") as f1:
#        f1.write(line+"\n")
    
    def parse(self, response):
        hxs = Selector(response)
        retracted = False
        retractedAndCited = False
        citedNotRetracted = False
        results = []
        paperCites = []
        info = []
        
        currentPaper = str(response.request.url)
        currentPaperId = currentPaper.rsplit('/', 1)[-1]
        
        retractedPapers = self.papers.keys()
        citedPapers = self.papers.values()
        
        if currentPaperId in retractedPapers:
          retracted = True # current paper has been retracted
          for papers in citedPapers: # citedPapers is a list of lists
            for paper in papers:
              if paper == currentPaperId:
                retractedAndCited = True # current paper has been retracted, cites another retracted paper
        if currentPaperId not in retractedPapers:
          citedNotRetracted = True #current paper cites a retracted paper, is not retracted itself
          
        # cases: 
        # paper is only retracted, does not cite another retracted paper
        # paper only cites a retracted paper, but has not been retracted
        # paper cites a retracted paper, is retracted itself
          
        if citedNotRetracted or retractedAndCited:
          for key, values in self.papers.iteritems():
            for paper in values:
              if paper == currentPaperId:
                paperCites.append(key) # we've found a retracted paper the current paper cites

        info.append(str(currentPaperId))
        
        #TO DO:
        '''
          create a list of the current paper id, the abstract, and the boolean flags
          append this list to the master results list
          for each list in the master results list, this is a new row in the csv
        '''                  

        abstracts = ''.join(hxs.xpath('//abstracttext//text()').extract())
        
        try:
          info.append(abstracts)
        except UnicodeEncodeError:
          info.append(abstracts.encode("utf-8"))
              
        if retracted:
          info.append('1')
        else:
          info.append('0')
        if citedNotRetracted or retractedAndCited:
          info.append('1')
        else:
          info.append('0')
          
#        info.append(paperCites)

        results.append(info)
        info = []
        

        for line in results:
          line[1].encode("utf-8")
          with open("ahh2.csv", 'a+') as f:
            text = csv.writer(f, delimiter=',')
            try:
              text.writerow(line)
            except UnicodeEncodeError:
#              print line
              convert = [l.encode("utf-8") for l in line]
              text.writerow(convert)
            
            
with open("ahh2.csv", 'a+') as output:
  writer = csv.writer(output)
  writer.writerow(["PaperId", "Abstract", "Retracted", "Cites", "Papers Cited"])