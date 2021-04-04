document.getElementById('button').addEventListener("click", function() {
	document.querySelector('.login').style.display = "flex";
});

document.querySelector('.close').addEventListener("click", function() {
	document.querySelector('.login').style.display = "none";
});