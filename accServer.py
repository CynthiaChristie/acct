

# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import cgi, cgitb
import re
import urllib.parse

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime



#
# Server - simple python example server that I'm trying to modify to suit.
#
class MyServer(BaseHTTPRequestHandler):
	def do_POST(self):
 	
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
 		
 		
		length = int(self.headers.get('content-length'))
		
		data = self.rfile.read(length)
	
		header, body, footer = splitPostData(data)
        

		newAcctCsv( getStrings(body) )

		resetDates()
		makeDisplaySet()		
		importHtml()


		for line in html:
			self.wfile.write(bytes(line, "utf-8"))
		
	def do_GET(self):
	
		print(self.path)
		
		if self.path[:len(accGraphUrl)] == accGraphUrl or self.path == "/accgraph.html":
		
			myUrl = urllib.parse.unquote(self.path)
			
			tail = re.findall("^.*?\?(.+)$",myUrl)
			
			if len(tail) == 1:
				tail = tail[0]
				
			whatType = re.findall("^type=(.+)$",tail)
			
			if len(whatType) == 1:
				whatType = whatType[0]
				
				 
			if whatType == "scatter":
				draw_line_plot()
			
			if whatType == "bar":
				draw_cat_plot()
				
			print("Sending accgraph.html")
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			for line in graphHtml:
				self.wfile.write(bytes(line, "utf-8"))			
		
		if self.path == "/" or self.path[:2] == "/?" or self.path == "/index.html" or self.path[:len(accHomeUrl)] == accHomeUrl:
		
			myUrl = urllib.parse.unquote(self.path)
		
			for regex in  [ ".+?\?(.+)#", ".+?\?(.+)$" ]:
				tail = re.findall(regex,myUrl)
	
				if len(tail) == 1:
					tail = tail[0]
					break
		
			newStartDate = globStrings.get("acctStartDate","")
			newEndDate = globStrings.get("acctEndDate","")
			
			if len(tail) == 0:
				tail = []
			else:
				tail = tail.split("&")
				
				form = re.findall("^form=(.+)$",tail[0])
				
				if len(form) == 1:
					form = form[0]
					tail.pop(0)
				else:
					form = ""
					
				print("Form: "+form)
				
				setFlag = False
				
				if form == "catFilter":
				
					action = re.findall("^action=(.+)$",tail[0])
					
					if len(action) == 1:
						tail.pop(0)
						if action[0] == "set":
							setFlag = True
					
					for item in acct:
						if item["Charge Date"] < globStrings["acctStartDate"] or item["Charge Date"] > globStrings["acctEndDate"] or item["Debit"] == "0.00":
							continue
						checkCategories[item["Category"]] = setFlag
							
						
					
						
					for item in tail:
					
						category = re.findall("^(.+)=set$",item)
						
						if len(category) == 1:
							category = plusToSpace(category[0])
							checkCategories[category] = True
						
				
				if form == "dateForm":
				
					for item in tail:

						start = re.findall("start=(.+)$",item)
						if len(start) == 1:
							newStartDate = start[0]
				
						end = re.findall("end=(.+)$",item)
						if len(end) == 1:
							newEndDate = end[0]					
				
				if form == "action":
					
					for item in tail:
					
						action = re.findall("action=(.+)$",item)
			
						if len(action) == 1:
							action = action[0]
					
							if action == "save":
								print("save")
								acctToCsv()
					
							if action == "reload":
								print("reload")
								importAcctCsv()
			
			
#                                 Leave this \/
		
			if newStartDate > newEndDate:
				trade = newStartDate
				newStartDate = newEndDate
				newEndDate = trade
				
			globStrings["acctStartDate"] = newStartDate
			globStrings["acctEndDate"] = newEndDate
				
			print("Sending index.html")
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			makeDisplaySet()	
			importHtml()

        
			for line in html:
				self.wfile.write(bytes(line, "utf-8"))
				
		if self.path == "/style.css":
			print("Sending style.css")
			self.send_response(200)
			self.send_header("Content-type","text/css")
			self.end_headers()
			
			for line in css:
				self.wfile.write(bytes(line, "utf-8"))
                
		if self.path[:len(accEntryUrl)] == accEntryUrl:
        
			tail = urllib.parse.unquote(self.path[len(accEntryUrl):])
			
			mods = list()
            
			tailElements = tail.split("&")
			
			
# THESE are the droids we're looking for!!!
# The form elements appear here via GET - They'll get passed to prepareAcctEntry via mods as designed!!
            
			for item in tailElements:

			
				k = re.findall("^key=(.*)$",item)
				if len(k) == 1:
					key = k[0]
					continue
                    
				i = re.findall("^index=(.*)$",item)
				if len(i) == 1:
					index = i[0]
					continue
                    
				mod = re.findall("^(.*)\=(.*)$",item)
				if len(mod) == 1:
					mod = mod[0]
					mods.append( mod )
                    

                  
			accHtml = prepareAcctEntry(key,index,mods)
            
			self.send_response(200)
			self.send_header("Content-type","text/html")
			self.end_headers()
            
			for line in accHtml:
				self.wfile.write(bytes(line, "utf-8"))
            
				
		if self.path == "/graph.png":
			
			data = getBinaryFile("graph.png");
					
			self.send_response(200)
			self.send_header("Content-type","image/png")
			self.end_headers();
			
			self.wfile.write(data)
			

#
# My functions for this script, beginning with...
#
#
# MASSAGE SERVER DATA
#
def getStrings(data):

	pData = data
	
	arr = list()
	thisStr = ""
	
	count = 0
	for char in pData:
		if count == len(pData):
			if len(thisStr) > 0:
				arr.append(thisStr)
				break
		if char == "\n":
			if len(thisStr) > 0:
				arr.append(thisStr)
				thisStr = ""
				count = count + 1
				continue
			else:
				count = count + 1
				continue
				
		thisStr = thisStr + char
		count = count + 1
		
		if count == len(pData):
			if len(thisStr) > 0:
				arr.append(thisStr)
				break
		
	return(arr)
    
def splitPostData(data):


    leading_nl = 4;
    trailing_nl = 2;

    nl=ord('\n')

    f_index = 0
    b_index = len(data) - 1

    count = 0

    while True:

        if f_index == len(data):
            print("Ran right off the end.")
            exit()
		
        if data[f_index] == nl:
            count = count + 1

        f_index = f_index + 1   
	
        if count == leading_nl:
            break

    count = 0

    while True:

        if( b_index == 0 ):
            print("Returned to start")
            exit()
		
        if data[b_index] == nl:
            count = count + 1				

        b_index = b_index - 1   
	
        if count == trailing_nl:
            break
		
    return(data[:f_index].decode("utf-8"),data[f_index:b_index].decode("utf-8"),data[b_index:].decode("utf-8"))

#
# PAGE AND RETURN OBJECT FUNCTIONS
#
def plusToSpace(s):

	t=""
	
	for item in s:
		if item == "+":
			t = t + " "
		else:
			t = t + item
			
	return(t)

def dollarsToCents(s):
	t = s.split(".")
	return( int(t[0])*100 + int(t[1]) )
	
def centsToDollars(c):

	s = str(int(c/100))+"."
	
	if c%100 < 10:
		s = s + "0"
		
	s = s + str(c%100)
	
	return(s)
		
def prepareAcctEntry(key,index,mods):

	Pdic = dict()
	categories = list()
    
    
    
	thisAcct = list()
	catDict = dict()
	
	for c in range(len(acct)):
    
		if ( acct[c]["Receipt-ID"] == key ) and ( acct[c]["Receipt-Index"] == index ):
			if acct[c]["Category"] == oldReceipts[key]["Anchor Category"]:
				eIndex = c
			else:
                		thisAcct.append(c)
                			
	
	anchor = dollarsToCents(acct[eIndex]["Debit"])
	
	transfer = 0
	
	collector = ""

	deleteFlag = False

	myHtml = list()
		
	for mod in mods:

		if mod[1] == "":
			continue

		if mod[0] == "dollars":
			transfer = transfer + int(mod[1])*100

		elif mod[0] == "cents":
			transfer = transfer + int(mod[1])

		elif mod[0] == "category" or mod[0] == "cattext":
			collector = plusToSpace(mod[1])
			
		elif mod[0] == "delete":
			if deleteFlag == True:
				continue
			deleteFlag = True
			transfer = dollarsToCents(acct[int(mod[1])]["Debit"])
			anchor = anchor + transfer
			transfer = 0
			acct[eIndex]["Debit"] = centsToDollars(anchor)
			print("debug:",len(acct))

			acct.pop(int(mod[1]))	
			print("entry "+mod[1]+ " popped")
			
			print("debug:",len(acct))
			

			foundFlag = False		
			for c in range(len(thisAcct)):

				if thisAcct[c] == int(mod[1]):
					foundFlag = True
					target = c
					print("Removed "+mod[1]+" from thisAcct")
					continue
				if foundFlag == True:
					thisAcct[c] = thisAcct[c] - 1
					print("thisAcct reduced",thisAcct[c]+1,"to",thisAcct[c])
					
			thisAcct.pop(target)



	if collector != "" and transfer > 0:
	
		if transfer > anchor:
			transfer = anchor

#
# This....? \/
		if catDict.get(collector,None) is not None:
			transfer = transfer + catDict[collector][1]
		
		anchor = anchor = anchor - transfer
	
		acct[eIndex]["Debit"] = centsToDollars(anchor)
	
		if catDict.get(collector,None) is not None:
			acct[catDict[collector][0]]["Debit"] = centsToDollars(transfer)
		else:
			dic = dict()
	
			dic["Charge Date"] = acct[eIndex]["Charge Date"]
			dic["Posted Date"] = acct[eIndex]["Posted Date"]
			dic["Vendor"] = acct[eIndex]["Vendor"]
			dic["Category"] = collector
			dic["Debit"] = centsToDollars(transfer)
			dic["Receipt-ID"] = acct[eIndex]["Receipt-ID"]
			dic["Receipt-Index"] = acct[eIndex]["Receipt-Index"]
			
			acct.append(dic)
			thisAcct.append(len(acct)-1)

	for item in acct:
		Pdic[item["Category"]] = None
        
	for k,v in Pdic.items():
		if k == oldReceipts[key]["Anchor Category"] or k == oldReceipts[key]["Default Category"]:
			continue
		categories.append(k)
        
	categories.sort()
	
	count = 0
	while count < len(categories):
		for item in thisAcct:
			if categories[count] == acct[item]["Category"]:
				catDict[categories[count]] = [ item, dollarsToCents(acct[item]["Debit"]) ]
				categories.pop(count)
				count = 0
				break
		count = count + 1
		
	categories.insert(0,oldReceipts[key]["Default Category"])
				
	
		
		
	fHand = open("accentry.html","r")
    
	
    
	for line in fHand:
		myHtml.append(line)
        
		if line.rstrip() == "<!--ACCTDATA-->":

#            jHand = open("acctentry.js","r")
#            for line in jHand:
#                myHtml.append(line)
#            jHand.close()
            
			category = acct[eIndex]["Category"] 
			if oldReceipts[key]["track"][0] > 1:
				category = category + " (" + str(int(acct[eIndex]["Receipt-Index"])+1) + " of " + str(oldReceipts[key]["track"][0]) + " identical transactions)"
            
			myHtml.append("<form id=\"inputWindow\" action=\"#\">\n")
            
			if len(thisAcct) > 0:
				myHtml.append("<p>Funds reassigned so far:</p>\n")
				myHtml.append("<table><tr><th style=\"text-align:left;\">Category</th>\n")
				myHtml.append("<th style=\"text-align: left;\">Amount</th></tr>\n")
                
				total = 0
                		
				for item in thisAcct:
					myHtml.append("<tr><td>" + acct[item]["Category"] + "</td><td>" + acct[item]["Debit"] + "</td>" +
"<td><a href=\"accentry.html?delete=" + str(item) + "&key=" + key + "&index=" + index + "\">DELETE</a></td></tr>\n")
					total = total + dollarsToCents(acct[item]["Debit"])
					
				myHtml.append("<hr><tr><td>Total</td><td>" + centsToDollars(total) + "</td>\n")
				myHtml.append("</table><hr>\n")

			if acct[eIndex]["Debit"] != "0.00":
				myHtml.append("<label for=\"dollars\">Enter an amount to reassign in dollars and cents: </label>\n")
				myHtml.append("<input type=\"number\" id=\"dollars\" name=\"dollars\" min=\"0\" max=\"" + acct[eIndex]["Debit"].split(".")[0] + "\">\n")
				myHtml.append("<input type=\"number\" id=\"cents\" name=\"cents\" min=\"0\" max=\"99\"><br>\n")

				myHtml.append("<label for \"category\"><br>Choose a category from the list:</label>\n")
				myHtml.append("<select name=\"category\" id=\"category\">\n")
				for item in categories:
					myHtml.append("<option value=\"" + item + "\">" + item + "</option>\n")
				myHtml.append("</select>\n")
            
				myHtml.append("<label for=\"cattext\">&nbsp;&nbsp;Or enter a new category here:</label>\n")
				myHtml.append("<input type=\"text\" id=\"cattext\" name=\"cattext\">\n")
				myHtml.append("&nbsp;&nbsp;<input type=\"submit\" value=\"Create Entry\">\n")

			myHtml.append("<input type=\"hidden\" name=\"key\" value=\"" + key + "\">\n")
			myHtml.append("<input type=\"hidden\" name=\"index\" value=\"" + index + "\">\n")
            
			myHtml.append("</form>\n")
			myHtml.append("<hr><div style=\"text-align: center;\"><a href=\"index.html?form=action&action=save\">Save and Return to Main Page</a></div>\n")
			myHtml.append("<div style=\"text-align: center;\"><a href=\"index.html?form=action&action=reload\">Discard Changes and Return</a></div>\n")
			myHtml.append("<script>\n")
            						
			myHtml.append("window.history.replaceState( { info: \"info\" }, \"accentry\", \"http://127.0.0.1:8080/accentry.html?key=" + key + "&index=" + index + "\");\n")
			
			myHtml.append("document.getElementById(\"inputWindow\").reset();\n")
			
			if acct[eIndex]["Debit"] != "0.00":
				myHtml.append("document.getElementById(\"dollars\").focus()\n")
            
			s = ""
			for item in acct[eIndex]["Vendor"]:
				if item != '"' and item !='#':
					s = s + item
            				
			myHtml.append("document.getElementById(\"vendor\").innerHTML = \"" + s +"\";\n")
			myHtml.append("document.getElementById(\"debit\").innerHTML = \"" + oldReceipts[key]["Debit"] +"\";\n")
			myHtml.append("document.getElementById(\"remain\").innerHTML = \"" + acct[eIndex]["Debit"] + "\";\n")
			myHtml.append("document.getElementById(\"charge\").innerHTML = \"" + acct[eIndex]["Charge Date"] +"\";\n")
			myHtml.append("document.getElementById(\"posted\").innerHTML = \"" + acct[eIndex]["Posted Date"] +"\";\n")
			myHtml.append("document.getElementById(\"category\").innerHTML = \"" + category +"\";\n")
			myHtml.append("document.getElementById(\"default\").innerHTML = \"" + oldReceipts[key]["Default Category"] + "\";\n")

			myHtml.append("document.getElementById(\"title\").innerHTML = \"Account Entry " + str(eIndex) +"\";\n")
			myHtml.append("</script>\n")

	fHand.close()     
	return(myHtml)
    
def importCss():

	css.clear()
		
	fHand = open("style.css","r")
	
	for line in fHand:
		css.append(line)
		
	fHand.close()
	
def importHtml():

	html.clear()
		
	fHand = open("index.html","r")
	jHand = open("acct.js","r")
	
	catFilterForm = "<div class=\"flexbox\">"

	catFilterForm = catFilterForm + "<a href=\"index.html?form=catFilter&action=set\" style=\"font-size: 14px;\">Set All</a>\n"	
	catFilterForm = catFilterForm + "<button type=\"submit\" form=\"catFilterForm\">Set Filter</button>\n"
	catFilterForm = catFilterForm + "<a href=\"index.html?form=catFilter&action=clear\" style=\"font-size: 14px;\">Clear All</a>\n"


	catFilterForm = catFilterForm + "</div><input type=\"hidden\" name=\"form\" value=\"catFilter\">\n"


	catFilterForm = catFilterForm + "<div class=\"flexbox\">\n"
	
	count = 0

	formCategories = dict()
	sortCategories = list()
	
	for item in acct:
		if item["Charge Date"] < globStrings["acctStartDate"] or item["Charge Date"] > globStrings["acctEndDate"] or item["Debit"] == "0.00":
			continue
		formCategories[item["Category"]] = None
			
	for k,v in formCategories.items():
		sortCategories.append(k)

	formCategories.clear()
	sortCategories.sort()
			
	for item in sortCategories:
		catFilterForm = catFilterForm + "<div><input type=\"checkbox\" id=\"cat" + item + "\" name=\"" + item + "\" value=\"set\" "
		if checkCategories[item] is True:
			catFilterForm = catFilterForm + "checked"
			
		catFilterForm = catFilterForm + ">\n" + "<label for=\"cat" + item + "\">" + item + "</label></div>\n"
		count = count + 1
		
	catFilterForm = catFilterForm + "</div>\n"
	
	for line in fHand:
		html.append(line)
		if line.rstrip() == "<!--ACCTDATA-->":

			html.append("<script>\n")
			html.append("var acctCount = "+str(len(displayAcct)) + ";\n")

			html.append("var acct = " + json.dumps(displayAcct) + ";\n")
			html.append("var catColors = " + json.dumps(catColorMaker()) + ";\n")
			
			html.append("document.getElementById(\"catFilterForm\").innerHTML = `" + catFilterForm + "`;\n")
			
			html.append("document.getElementById(\"dateRangeForm\").innerHTML = `" +
			"<input type=\"hidden\" name=\"form\" value=\"dateForm\">\n" +
			"<label for=\"start\">Start Date</label>\n" +
			"<label for=\"end\">End Date</label>\n" +
			"<input type=\"date\" id=\"start\" name=\"start\" min=\"" + globStrings["acctMinStartDate"] +
				"\" max=\"" + globStrings["acctMaxEndDate"] + "\">\n" +
			"<input type=\"date\" id=\"end\" name=\"end\" min=\"" + globStrings["acctMinStartDate"] +
				"\" max=\"" + globStrings["acctMaxEndDate"] + "\">\n" +
				"<br><input type=\"submit\" value=\"Set\">\n" +
				"<br><a href=\"index.html?form=dateForm&start=" + globStrings["acctMinStartDate"] +
				"&end=" + globStrings["acctMaxEndDate"] + "\">Reset</a>\n" +
			"</form>`;\n")

			html.append("document.getElementById(\"displayDates\").innerHTML = \"" + globStrings["acctStartDate"] + " - " + globStrings["acctEndDate"] + "\";\n")


			html.append("var acctStatus = \"Status : " + globStrings["acctStatus"] + "\";\n")			
			html.append("document.getElementById(\"acctStatus\").innerHTML = acctStatus;\n")
			
			
            
            
			for line in jHand:
				html.append(line)
			html.append("</script>\n")
			
	fHand.close()
	jHand.close()

def getBinaryFile(name):

	fHand = open(name,"rb")
	buf = fHand.read()
	fHand.close()
	
	return(buf)

#
# ACCT FUNCTIONS
#

def initDatesBlank():
	globStrings["acctStartDate"] = ""
	globStrings["acctEndDate" ] = ""
	globStrings["acctMinStartDate"] = ""
	globStrings["acctMaxEndDate" ] = ""
		
		
def importAcctCsv():
# Here we don't need all the code to do with OldReceipts because this is existing data.

	acct.clear()
	displayAcct.clear()
	
	try:
		fHand = open("acc.csv","r")
	except:
#This is a new data set, just go back and and see if the user uploads
		globStrings["acctStatus"] = "No data files.  Try uploading new data."
		initDatesBlank()
		return
    
#	newEntry = dict()
    
	for line in fHand:
		newEntry = dict()
		arr = line.rstrip().split(",")
        
		if arr[0] == "Charge Date":
			continue
            
		newEntry["Charge Date"] = arr[0]
		newEntry["Posted Date"] = arr[1]
		newEntry["Vendor"] = arr[2]
		newEntry["Category"] = arr[3]
		newEntry["Debit"] = arr[4]
		newEntry["Receipt-ID"] = arr[5]
		newEntry["Receipt-Index"] = arr[6]
        
		acct.append(newEntry)
        
	fHand.close()

	if len(acct) == 0:
		globStrings["acctStatus"] = "Database is empty."
		initDatesBlank()
		return
		
	setCategoryCheck()
	resetDates()
	makeDisplaySet()
    
	globStrings["acctStatus"] = "Loaded " + str(len(acct)) + " records."
    
def resetDates():

	if len(acct) == 0:
		globStrings["acctStatus"] = "Nothing to display"
		return
		
	acct.sort(key = lambda x : x["Charge Date"])
	
	globStrings["acctMinStartDate"] = acct[0]["Charge Date"]
	globStrings["acctMaxEndDate"] = acct[len(acct)-1]["Charge Date"]
	
	globStrings["acctStartDate"] = acct[0]["Charge Date"]
	globStrings["acctEndDate"] = acct[len(acct)-1]["Charge Date"]
	
		
def acctToCsv():

	bookFhand = open("acc.csv","w")
	
	bookFhand.write("Charge Date,Posted Date,Vendor,Category,Debit,Receipt-ID,Receipt-Index\n")
	for item in acct:
	
		bookFhand.write(
		item["Charge Date"]+","+
		item["Posted Date"]+","+
		item["Vendor"]+","+
		item["Category"]+","+
		item["Debit"] +","+
		item["Receipt-ID"] + "," +
		item["Receipt-Index"] + "\n" )

	bookFhand.close()

	
def receiptToCsv():
	
	recFhand = open("receipt.csv","w")
	
   
	for k, v in oldReceipts.items():
		recFhand.write( k + "," + str(v["track"][0]) + "," + v["Default Category"] + "," + v["Debit"] + "," + v["Anchor Category"] + "\n" )
	recFhand.close()
		

def getOldReceipts():

	try:
		recFhand = open("receipt.csv","r")
	except:
		globStrings["acctStatus"] = "No existing transactions found in database. "
		return
        
	for line in recFhand:
		arr=line.strip().split(",")
		oldReceipts[arr[0]] = dict()
		oldReceipts[arr[0]]["track"] = [ int(arr[1]), 0 ]
		oldReceipts[arr[0]]["Default Category"] = arr[2]
		oldReceipts[arr[0]]["Debit"] = arr[3]
		oldReceipts[arr[0]]["Anchor Category"] = arr[4]
	recFhand.close()

 
def createCcEntry(line):
# This takes the raw csv entry from Captial one and returns a dictionary with the labels I use, but the values unaltered.
# Note that this function does not check to see if the transaction is in already.

	arr = line.strip().split(",")
	entry = dict()
	
	for label in ccCsvLabels:
		try:
			entry[label] = arr[0]
		except:
			globStrings["acctStatus"] = "Tried to load invalid data set."
			return False
		arr.pop(0)
        	  
# This next bit with Receipt-ID is confusing because I repurposed that field.  It actually filters out credits.
	if len(entry["Receipt-ID"]) > 0:
		return False
		
# I repurposed this one too, it was "Card no." but that's always the same for me.
	entry["Default Category"] = entry["Category"]
	
	for regex, category in reCategorizeVendor.items():

		arr=re.findall(regex,entry["Vendor"])
		if len(arr) == 0:
			continue

		entry["Category"] = category
		break
# /\ break is because we aren't going to recategorize the same vendor
		


	for regex, category in reCategorizeCategory.items():
	
		arr=re.findall(regex,entry["Category"])
		if len(arr) == 0:
			continue

# Never overwrite the original Default Category	
	if entry.get("Default Category", "") == "":
		entry["Default Category"] = entry["Category"]		

		entry["Category"] = category
#do not break here - we may well recategorize a category, to store the default

	return(entry)
	
    
def catColorMaker():
	
	colorList = list()
	
	for item in displayAcct:
		colorList.append(activeCategories[item["Category"]]["color"])	

		
	return(colorList)
	
				
def newAcctCsv(data):

	try:
		header = data[0].rstrip().split(",")
	except:
		globStrings["acctStatus"] = "Unable to load any data at all from that file"
		return False;

	ccLabels = [ "Transaction Date", "Posted Date", "Card No.", "Description", "Category", "Debit", "Credit" ]
	
	if header != ccLabels:
		globStrings["acctStatus"] = "This does not look like a Capital One csv header."
		return False
		
	

	data.pop(0)
    
	ccBook = list()
	
	print("Received",len(data),"entries from upload.")
	entries = 0
	
	for line in data:

		arr = createCcEntry(line)

		if arr is False:
			continue
    
		ccBook.append(arr)
		
		entries = entries + 1
		
	print("Entries from upload data: ",entries)

	entries = 0

	for entry in ccBook:
        
		r = entry["Charge Date"] + entry[ "Posted Date" ] + entry["Vendor"] + entry["Debit"]
		receiptTag=""
		
		for item in r:
			if item.isalpha() or item.isnumeric():
				receiptTag = receiptTag + item
			
# If new and unique so far	
# Creates a new accounting entry   
		if oldReceipts.get(receiptTag,None) is None:
			entry["Receipt-ID"] = receiptTag
			entry["Receipt-Index"] = "0"
 

			oldReceipts[receiptTag] = dict()
			oldReceipts[receiptTag]["track"] = [ 1, 1 ]
			oldReceipts[receiptTag]["Default Category"] = entry["Default Category"]
			oldReceipts[receiptTag]["Debit"] = entry["Debit"]
			oldReceipts[receiptTag]["Anchor Category"] = entry["Category"]
			acct.append(entry)
			entries = entries + 1
			continue
            
# If new but an identical transaction exists from this load. (Bus tickets!)

		if oldReceipts[receiptTag]["track"][0] == oldReceipts[receiptTag]["track"][1]:
			entry["Receipt-ID"] = receiptTag
			entry["Receipt-Index"] = str(oldReceipts[receiptTag]["track"][0])

			
			oldReceipts[receiptTag]["track"][0] = oldReceipts[receiptTag]["track"][0] + 1
			oldReceipts[receiptTag]["track"][1] = oldReceipts[receiptTag]["track"][1] + 1


			acct.append(entry)
			entries = entries + 1
			continue
        
# Or, we're finding the one(s) that existed on disk already.
# Counts them only.
		oldReceipts[receiptTag]["track"][1] = oldReceipts[receiptTag]["track"][1] + 1
       
	acctToCsv()
	receiptToCsv()
	
	setCategoryCheck()
	resetDates()
	makeDisplaySet()
	
	return True



def makeDisplaySet():

	displayAcct.clear()
	displayPandas.clear()
	
	displayAcctTotal = 0
	
	for item in acct:
		checkCategories[item["Category"]] = checkCategories.get(item["Category"],True)
		if item["Charge Date"] < globStrings["acctStartDate"] or item["Charge Date"] > globStrings["acctEndDate"] or item["Debit"] == "0.00" or checkCategories[item["Category"]] is False:
			continue	
		displayAcct.append(item)
		displayAcctTotal = displayAcctTotal + 1
		
		for k,v in item.items():
			displayPandas[k] = displayPandas.get(k,list())
			displayPandas[k].append(v)
			
		
	globStrings["acctStatus"] = "Loaded " + str(displayAcctTotal) + " records."

	activeCategories.clear()
	
	totalCents = 0
	
	for item in displayAcct:
		activeCategories[item["Category"]] = activeCategories.get(item["Category"],dict())
	
		activeCategories[item["Category"]]["count"] = activeCategories[item["Category"]].get("count",0) + 1
		activeCategories[item["Category"]]["cents"] = activeCategories[item["Category"]].get("cents",0) + dollarsToCents(item["Debit"])
		
		totalCents = totalCents + dollarsToCents(item["Debit"])
		
	for k,v in activeCategories.items():
	
		red = min(255, int( 1.8 * (( 255 * v["cents"] ) / totalCents )) )
		blue = min(255, int( 1.8 * (( 255 * v["count"] ) / len(displayAcct) )) )
		
		v["color"] = "rgba(" + str(red) + ",32," + str(blue) + ",1)"
		
	
		
def setCategoryCheck():

	for item in acct:
		checkCategories[item["Category"]] = checkCategories.get(item["Category"],True)
				
		


#
# Graph functions
#

def draw_line_plot():

	fileName = "graph.png"
	
	centsTotal = 0
	
	for item in displayAcct:
		centsTotal = centsTotal + dollarsToCents(item["Debit"])
		
	graphDict = dict()
	
	graphDict["Charge Date"] = displayPandas["Charge Date"]
	graphDict["Category"] = displayPandas["Category"]
	graphDict["Debit"] = displayPandas["Debit"]
	
	
	use_df = pd.DataFrame.from_dict(graphDict)
	use_df["Debit"] = pd.to_numeric(use_df["Debit"])
#	outlierQ = 0.9
	
	use_df = use_df.groupby([ "Charge Date", "Category" ], as_index=False).sum()
	
	print(use_df)
	
#	tooBig_df = use_df[use_df["Debit"]>use_df["Debit"].quantile(outlierQ)]


#	tooBig_df = tooBig_df.sort_values("Charge Date")
	
#	tooBig_df = tooBig_df.pivot(index="Charge Date", columns="Category", values="Debit")
	
	


#	tb = json.loads(tooBig_df.to_json())
	

#	footNote =  [ "Not Included in Graph" ]
#	footIndex = 0
#	count = 0
#	outlierDat = []
	
	
#	for k0,v0 in tb.items():
#		for k1,v1 in v0.items():
#			if v1 is None:
#				continue
#			outlierDat.append([ k0, k1, v1 ])

#	outlierDat.sort(key = lambda x: x[0])
#	outlierDat.sort(key = lambda x: x[1])
#	outlierDat.sort(reverse = True, key = lambda x: float(x[2]))	
			
#	for item in outlierDat:
#		footNote[footIndex] = footNote[footIndex] + " - " + item[0] + " (\$"+floatToDollar(item[2]) + " on " + datetime.utcfromtimestamp(int(item[1])/1000).strftime("%m-%d")+ ")"
#		count = count + 1
#		if count == 3:
#			count = 0
#			footIndex = footIndex + 1
#			footNote.append("")

			
#	print(footNote)
#	exit()
	
#	use_df = use_df[use_df["Debit"]<=use_df["Debit"].quantile(outlierQ)]

#	print(tooBig_df)
#	exit()

	use_df=use_df.pivot(index="Charge Date", columns="Category", values="Debit")
#	use_df = use_df.fillna(0.0)

	fileName = "graph.png"
			
	fig, ax = plt.subplots(figsize=(15,8))
	plt.tick_params(axis="both", which="major", labelsize=8)
#	plt.xticks(rotation=-30)

	plt.subplots_adjust(bottom=0.2)
	plt.subplots_adjust(left=0.05)
	plt.subplots_adjust(right=0.8)

	plt.xticks(rotation=45)
	
	
	scat = sns.scatterplot(data=use_df,s=70)
	
	scat.axes.set_title(globStrings["acctStartDate"] + " to " + globStrings["acctEndDate"] + "  (Total: $" + centsToDollars(centsTotal) + ")",fontsize=30)
	plt.legend(bbox_to_anchor=(1.02,1), loc="upper left", borderaxespad=0)

#	footY = max(0.05 + 0.02 * len(footNote),0.07)
	
#	for note in footNote:
#		while note[0] == " " or note[0] == "-":
#			note = note[1:]
#		plt.figtext(0.5,footY,note,ha="center",fontsize=9)
#		footY = footY - 0.02
		
	ax.set(xlabel=None,ylabel=None)
		
	fig.savefig(fileName)
	
def draw_cat_plot():

	
	fileName = "graph.png"
	
	centsTotal = 0
	
	for item in displayAcct:
		centsTotal = centsTotal + dollarsToCents(item["Debit"])
		
	graphDict = dict()
	
	graphDict["Category"] = displayPandas["Category"]
	graphDict["Debit"] = displayPandas["Debit"]
	
	df = pd.DataFrame.from_dict(graphDict)
	
	df["Debit"] = pd.to_numeric(df["Debit"])

	df_cat=df.groupby( [ "Category" ],as_index=False).sum()

		
	fig, ax = plt.subplots(figsize=(14,7),dpi=75)


	
	plt.tick_params(axis="both", which="major", labelsize=8)
	ax.set_xticklabels(ax.get_xticklabels(),rotation=20, ha="right")
	
#	plt.tight_layout()
	bar = sns.barplot(data=df_cat,x="Category",y="Debit",palette="tab10")

	bar.axes.set_title(globStrings["acctStartDate"] + " to " + globStrings["acctEndDate"] + "  (Total: $" + centsToDollars(centsTotal) + ")",fontsize=30)
#	ax.set(title=globStrings["acctStartDate"] + " to " + globStrings["acctEndDate"],fontsize=30)
	
	ax.set(xlabel=None,ylabel=None)
		
	fig.savefig(fileName)


def importGraphUrl():

	fHand = open("accgraph.html" , "r")
	
	for line in fHand:
		graphHtml.append(line)
		
	fHand.close()
	
#
# GLOBAL OBJECTS

	
reCategorizeVendor = {
"^7 ELEVEN.*": "Convenience Store",
"^HUSKY.*": "Convenience Store",
"^PETROCAN.*": "Convenience Store",
"^CALGARY TRANSIT.*": "Bus",
"^AIRBNB.*": "Housing",
"^Spotify.*": "Entertainment" ,
"^VESTA.*CHATR.*": "Phone",
".*[Ll][Ii][Qq][Uu][Oo][Rr].*": "Drinking",
"^LEAF LIFE.*": "Cannabis",
".*[Cc][Aa][Nn][Nn][Aa][Bb][Ii][Ss].*": "Cannabis",
"^SAFEWAY.*": "ACCT",
"^GOOGLE.*": "ACCT",
"^ENTERPRISE.*": "ACCT"
}

reCategorizeCategory = {
"^Gas/Automotive.*": "Convenience Store",
"^Convenience Store.*": "ACCT",
"^Merchandise.*": "ACCT",
"^Health Care.*": "ACCT",
"^Dining.*": "ACCT",
".*[Oo][Tt][Hh][Ee][Rr].*": "ACCT"
}

ccCsvLabels = [ "Charge Date" , "Posted Date" , "Default Category", "Vendor" , "Category" , "Debit" , "Receipt-ID" ]
	
accEntryUrl = "/accentry.html?"
accHomeUrl = "/index.html?"
accGraphUrl = "/accgraph.html?"

	
html = list()
css = list()

acct = list()
displayAcct = list()
displayPandas = dict()

oldReceipts = dict()

globStrings = dict()

activeCategories = dict()

checkCategories = dict()

graphHtml = list()

getOldReceipts()
importAcctCsv()


# Do this when it's time to send it, index.html is not static
#importHtml()
importCss()

importGraphUrl()

hostName = "localhost"
serverPort = 8080






if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
