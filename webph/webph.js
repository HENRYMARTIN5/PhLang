// Injects brython, brython stdlib, and webph.py

fetch("https://cdnjs.cloudflare.com/ajax/libs/brython/3.9.5/brython.min.js").then(txt => {eval(txt);});
fetch("https://cdnjs.cloudflare.com/ajax/libs/brython/3.9.5/brython_stdlib.min.js").then(txt => {eval(txt);});
