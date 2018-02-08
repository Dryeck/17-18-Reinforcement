board = "{{board}}"

var colorDict = {
	"X":"red",
	"O":"blue"
};

function play(x, y) {
	board += "(" + x + "," + y + ")X;"
	document.getElementById("moveForm").value = board;
	x = document.getElementById("sub");
	x.click();
}

function color(board) {
	var moves = board.split(";");
	var numMoves = moves.length;
	for(var i = 0; i < numMoves - 1; i++) {
	  	var symbol = moves[i].split(")")[1];
	  	var aux = moves[i].split(")")[0].split("(")[1].split(",");
	  	var x = aux[0];
	  	var y = aux[1];
	  	var cellID = "";
	  	cellID += x + "-" + y;
	  	var color = colorDict[symbol];
	  	console.log("Trying to set color of cell with id " + cellID);
	  	var cell = document.getElementById(cellID);
	  	cell.style.backgroundColor = color;
		}
}
window.onload = function() {
	color(board);
	var outcome = "{{outcome}}";
	console.log(outcome);
	if (outcome == "Win") {
	  	document.getElementById("win").style.display = "block";
	  	document.getElementById("restart").style.display = "";
	}
	if (outcome == "Loss") {
	  	document.getElementById("lost").style.display = "block";
	  	document.getElementById("restart").style.display = "";
	}
}