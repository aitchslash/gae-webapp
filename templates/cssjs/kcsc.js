/* kcsc javascript */

/*
window.onload = function() {
	document.getElementById("monday").innerHTML=mondayText;
	toggleMon();
}
*/

monToggle = true //may need to use 0, increment when toggled, %2 == 0 to determine toggle status
tuesToggle = true

function toggleMon() {
	if (monToggle == false) {
		document.getElementById("monday").innerHTML=mondayText;
		monToggle = true;
	} else {
		document.getElementById("monday").innerHTML=altMondayText;
		monToggle = false;
	}
}

var mondayText = "<li><h4>MONDAYS</h4></li><li>9:30 Keep Fit w/ Zumba Gold</li><li>1:00 Bridge</li><li>7:30 Badminton @ KC P.S.</li>";
var altMondayText = "<h4>MONDAYS</h4><h4>Keep Fit w/ Zumba Gold @ 9:30am</h4>" +
	"A 10 week session of classes starts Jan12th under the " +
	"leardership of Deanna, an excellent instructor. The fee " +
	"for the session is $40.00, payable upon registration. The " +
	"regular user fee for the Centre is $1.00.<br><br>" +
	"<h4>1:00 Bridge</h4><br>" +
	"<h4>Badminton @ 7:30pm</h4> This activity resumes January 6th. " +
	"If you feel fit and would like a bit of exercise, make a note and come and join us " +
	"Monday evenings at the King City Public School. If you don't know how to play, we will " +
	"teach you and we'll even provide you with a racket if needed. the fee is $1.00 "+
	"which goes toward the rental of the school gym and cost of the birdies.";

function toggleTues() {
	if (tuesToggle == false) {
		document.getElementById("tuesday").innerHTML=tuesdayText;
		tuesToggle = true;
	} else {
		document.getElementById("tuesday").innerHTML=altTuesdayText;
		tuesToggle = false;
	}
}
var tuesdayText = "<li><h4>TUESDAYS</h4></li><li>10:00 Bowling @ Pro Bowl Lanes, Richmond Hill</li><li>1:00 Bid Euchre</li>";
var altTuesdayText = "<h4>TUESDAYS</h4><h4>5 Pin Bowling @ 10:00am</h4>" +
	"The new season is well underway at the Pro Bowl Lanes in Richmond Hill. It's all about " +
	"fun and the bowling gang certainly have a lot of it. There's plenty of surprises each week " +
	"including high and low scores, plus odd things you've never seen before. Should you require " +
	"transportation, just call Vic Warner. The fee is $4.50 for three games. Bowling " +
	"shoes are free. If interested call Mary McDougall" +
	"<h4>Bid Euchre @ 1:00pm</h4>" +
	"Bid euchre is now in full swing and any new members are warmly welcomed. If you're a " +
	"new player, someone will teach and assist you. the fee is $2.00" +
	"Contact Vince Cancelli";