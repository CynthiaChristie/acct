/*
**
** We inherit an array of objects "acct"
*/

	
	function sortAcct(sortBy) {
	
		var c;
		var d;
		var obj;
		var aObj;
		var bObj;
		
	/*	console.log("Sorting acct by "+sortBy); */
	
		if(acct.length == 0) {
			return;
		}
		
	
		for(c = 0; c < acct.length ; c++ ) {
			for(d = 0 ; d < acct.length - c - 1 ; d++ ) {
				aObj = acct[d][sortBy];
				bObj = acct[d+1][sortBy];
			/*	console.log(aObj + " " + bObj); */
				if (sortBy == "Debit" ) {
					aObj = parseFloat(aObj);
					bObj = parseFloat(bObj);
				}			
				if (aObj > bObj) {
			/*		console.log(acct[d],acct[d+1]); */
					obj = acct[d];
					acct[d] = acct[d+1];
					acct[d+1] = obj;
			/*		console.log(acct[d],acct[d+1]); */
				}
			}
		}
	}

	function sortAcctByCharge() {
		sortAcct("Charge Date");
		tableToHtml();
	}
	
	function sortAcctByPosted() {
		sortAcct("Posted Date");
		tableToHtml();
	}
	
	function sortAcctByVendor() {
		sortAcct("Vendor");
		tableToHtml();
	}
	
	function sortAcctByCategory() {
		sortAcct("Category");
		tableToHtml();
	}
	
	function sortAcctByDebit() {
		sortAcct("Debit");
		tableToHtml();
	}
	
	function padWithSpaces(s,num,dir) {
		
		var hasSpaces=s;
		var c;
		
		if ( s.length >= num ) {
			return(hasSpaces);
		}
		
		for( c = 0; c < (num - s.length); c++ ) {
			if(dir==0) {
				hasSpaces = " " + hasSpaces;
			} else {
				hasSpaces = hasSpaces + " ";
			}
		}
		
		return(hasSpaces);
	}
		
	function tableToHtml() {
	
		var x;
		var linkRef = "";
		var displayText = "";
		var acctHtml = "";
		
		for ( x=0 ; x < acct.length ; x++ ) {
			linkRef = "accentry.html?key=" + acct[x]["Receipt-ID"] + "&index=" + acct[x]["Receipt-Index"]

			acctHtml = acctHtml + "<a href=\"" + linkRef + "\"><pre>" +
			padWithSpaces(acct[x]["Charge Date"],15,1) +
			padWithSpaces(acct[x]["Posted Date"],15,1) +
			padWithSpaces(acct[x]["Vendor"],30,1)      +
			padWithSpaces(acct[x]["Category"],15,1)    +
			padWithSpaces(padWithSpaces(acct[x]["Debit"],7,0),15,1) + "</pre></a>\n";
			

		}
	
		acctHtml = acctHtml + "";
	
		document.getElementById("acctwindow").innerHTML = acctHtml;
		console.log(acctHtml);	
	}
	
	tableToHtml();
	

	/*
	sortAcctByDebit();
	sortAcctByVendor();
	sortAcctByCategory();
	sortAcctByCharge();
	*/
	
