'''		CREATED BY GAURAV MITRA		'''
'''		CRAWLS AND SCRAPES GOOGLE SCHOLAR WEBSITE ON ENTERING A QUERY
                WORKS IN PYTHON 2.6+ AND ALSO IN DISTRIBUTIONS LIKE ANACONDA
                BUT NOT IN PYTHON 3                '''
# WARNINGS :  
# 		1)		GOOGLE SCHOLAR robots.txt SITE CLEARLY FORBIDS CRAWLERS AND SCRAPERS.
#		2)		MOST OF THE DATA IN GOOGLE SCHOLAR IS INVISIBLE TO ROBOTS AND CRAWLERS
#		3)		HENCE TOO MUCH QUERYING MAY LEAD TO TEMPORARY BAN ON YOUR IP ADDRESS

'''		LIGHTWEIGHT NON-RECURSIVE CRAWLER THAT CRAWLS THROUGH THE GOOGLE SCHOLAR SITE MOSTLY RESPECTING GOOGLE TERMS OF USE BUT MAY LEAD TO 
		OCCASSIONAL VIOLATION OF THE robots.txt OF GOOGLE SCHOLAR '''

try :
	import urllib
	import urllib2
	#import BeautifulSoup as bs
	import re
	import random
	import robotparser as rp
	import htmlentitydefs
	import hashlib
	import sys
	import os
	import datetime
	import time
except ImportError:
	print 'ERROR : {}\n{}'.format("SOME OF THE MODULES REQUIRED IS ABSENT. PLEASE RE-INSTALL PYTHON OR FIX IT","-----")

'''     RETURNS SOME CONSTANTS ESSENTIAL FOR CRAWLING GOOGLE SCHOLAR SITE       '''
'''     RETURN TYPE : GOOGLE SCHOLAR MAIN PAGE AND QUERY STRING         '''
def initialization() :
        return "http://scholar.google.com","/scholar?q="

'''     A SIMPLE ROBOTPARSER THAT ABIDES BY ROBOTS.TXT OF THE GOOGLE SCHOLAR SITE https://scholar.google.co.in/robots.txt       '''
'''     ITS ALWAYS GOOD TO ABIDE BY RULES      '''
'''     RETURN TYPE : TEXT FROM ROBOTS.TXT      '''
def parse_Robot_File():
	robot=rp.RobotFileParser()
	GOOGLE_SCHOLAR_MAIN_URL,QUERY_APPEND=initialization()
	robot.set_url(GOOGLE_SCHOLAR_MAIN_URL+"/robots.txt")
	return robot.read()

'''     A PSEUDO-RANDOM NUMBER SEED SETTER     '''
'''     USES DATETIME OBJECT (CURRENT TIME IN MILLISECOND) AS SEED TO ENSURE UNIQUE PSEUDORANDOM NUMBER IS GENERATED EVERY TIME         '''
def random_number_seedset() :
	date=datetime.datetime.now()
	time_since_epoch=time.mktime(date.timetuple()) + date.microsecond/1000000.0
	milliseond=time_since_epoch*1000
	random.seed(milliseond)
	
'''     CREATES A FAKE GOOGLE ID        '''
'''     USES MD5 ALGORITHM TO PRODUCE A 128 BIT HASH VALUE OF WHICH ONLY 16 DIGIT HEXADECIMAL IS TAKEN INSTEAD OF 32    '''
'''     RETURN TYPE : A DICTIONARY CONTAINING THE HEADER WITH User-Agent and Cookies AS THE KEYS        '''
def create_fake_id() :
	random_number_seedset()
	random_string=str(random.random())
	random_string=random_string.encode('utf8')
	fake_google_id=hashlib.md5(random_string)
	fake_google_id=fake_google_id.hexdigest()
	fake_google_id=fake_google_id[:16]
	HEADERS=dict()
	HEADERS['User-Agent']='Mozilla/5.0'
	HEADERS['Cookie']='GSP=ID={}:CF=4'.format(fake_google_id)
	return HEADERS

'''     FUNCTION WHICH QUERIES GOOGLE SCHOLAR SITE      '''
'''     RETURN TYPE : LIST OF CITATIONS         '''
def Google_Scholar_Query(searchQuery):
        HEADERS=create_fake_id()
        GOOGLE_SCHOLAR_URL,QUERY_APPEND=initialization()
        searchQuery=searchQuery.replace(" ","+")
        url = GOOGLE_SCHOLAR_URL + QUERY_APPEND + searchQuery
        html=""
        try :
                request = urllib2.Request(url, headers=HEADERS)
                response = urllib2.urlopen(request)
                page_data = response.read()
                page_data = page_data.decode('utf8')
                html=page_data
        except urllib2.HTTPError : 
                print '{0}'.format("HTTP 503 SERVICE UNAVAILABLE ERROR")
                print '{0}'.format("-----------------------------------")
                print '{0}'.format("POSSIBLE REASONS")
                print '{0}'.format("------------------")
                print '{0}1 : {1}'.format("\t","CHANGE USER-AGENT IN HEADERS TO FIX THE ERROR")
                print '{0}2 : {1}'.format("\t","GOOGLE SCHOLAR HAS DETECTED THAT THIS IS A ROBOT AND TEMPORARILY BLOCKED ROBOTS FROM THIS IP")

        link_parse = re.compile(r'<a href="(/scholar\.bib\?[^"]*)')
        links = link_parse.findall(html)
        links = [re.sub('&(%s);' % '|'.join(htmlentitydefs.name2codepoint), lambda m: chr(htmlentitydefs.name2codepoint[m.group(1)]), item) for item in links]

        output = list()
        for link in links:
                #       UNCOMMENT THIS REGION IF YOU WANT TO RESPECT GOOGLE TERMS OF SERVICE https://scholar.google.co.in/robots.txt
                #       IT IS ALWAYS A GOOD PRACTICE TO DO SO
                
                '''if not allowed_By_Robots(link) :
                        continue'''
                url = GOOGLE_SCHOLAR_URL+link
                try :
                        request = urllib2.Request(url, headers=HEADERS)
                        response = urllib2.urlopen(request)
                        bibtex = response.read()
                        bibtex = bibtex.decode('utf8')
                        output.append(bibtex)
                except urllib2.HTTPError :
                        print '\n{0}'.format("HTTP 503 SERVICE UNAVAILABLE ERROR")
                        print '{0}'.format("-----------------------------------")
                        print '{0}'.format("POSSIBLE REASONS")
                        print '{0}'.format("------------------")
                        print '{0}1 : {1}'.format("\t","CHANGE USER-AGENT IN HEADERS TO FIX THE ERROR")
                        print '{0}2 : {1}'.format("\t","GOOGLE SCHOLAR HAS DETECTED THAT THIS IS A ROBOT AND TEMPORARILY BLOCKED ROBOTS FROM THIS IP")
                        continue
        return output

'''     CHECK IF THE LINK IS PERMITTED BY THE ROBOTS.TXT OF GOOGLE SCHOLAR      '''
'''     RETURN TYPE : BOOLEAN VALUE TRUE IF IT IS ALLOWED ELSE FALSE    '''
def allowed_By_Robots(link):
	robot=parse_Robot_File()
	if (robot.can_fetch("*",link) is True) :
		return True
	else :
		return False

'''     JUST PRINTS THE SEARCH QUERIES AND THEIR RELEVANT DATA TO THE COMMAND LINE OR THE CONSOLE       '''
def Output_Citations(citations) :
        print '\n{}\n{}'.format("\tOUTPUT","\t------\n")
        for citation in citations :
                print citation
                
'''     WRITING ALL THE RELEVANT DATA TO A FILE WHOSE NAME IS SPECIFIED BY THE USER     '''
def FileWrite(citations) :
        print '\n{}\n{}'.format("\tENTER THE FILENAME : ","\t------------------\n")
        filename=raw_input("THE NAME OF THE FILE (NO EXTENSIONS WILL LEAD TO DEAFULT .txt FILE)  : ")
        pattern=re.compile(r'\.')
        if not pattern.findall(filename) :
               filename=filename+".txt"
        filewrite=open(filename,'w+')
        for citation in citations :
                filewrite.write(citation)
        filewrite.close()

'''     MAIN FUNCTION           '''
if __name__=="__main__" :
        print '{}'.format("WELCOME TO GOOGLE SCHOLAR CRAWLER AND DATA SCRAPER")
        print '{}'.format("--------------------------------------------------")
        print "{}".format("\n")
        print '{0}\n{1}\n\n\t1 : {2}\n\t2 : {3}\n\t3 : {4}\n'.format("YOU CAN ENTER THE FOLLOWING QUERIES","---------------------------","NAME OF THE PAPER","NAME OF THE AUTHOR","ANY KEYWORD OF THE PAPER")
        query=raw_input("\tSEARCH :: ")
        citations_list=Google_Scholar_Query(query)
        if(len(citations_list) != 0 ) :
                print '{}\n{}\n'.format("\tSEARCH SUCCESSFUL","\t-----------------")
                print '\t1 : {}\n\t2 : {}\n'.format("PRESS 1 TO SHOW LIST OF CITATIONS","PRESS 2 TO WRITE THEM INTO A FILE")
                choice=int(raw_input("\t ENTER YOUR CHOICE :: " ))
                if (choice == 1) :
                        Output_Citations(citations_list)
                else :
                        FileWrite(citations_list)
        print '\n{}'.format("x----------x-----------------END-----------------x----------x")
