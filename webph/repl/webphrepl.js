//    Copyright (C) 2022 Henry Martin 
//    This program comes with ABSOLUTELY NO WARRANTY. 
//    This is free software, and you are welcome to redistribute it 
//    under certain conditions; see the LICENSE file for details. 
console.log(
    "%c webPH %c v0.0.1 alpha",
    "border-radius: 3px 0px 0px 3px; padding: 1%; font-size:1.3em; font-weight: 500; background-color: #00796A; font-family: Google Sans; sans-serif; color: white",
    "border-radius: 0px 3px 3px 0px; padding: 1%; font-size:1.3em; font-weight: 400; background-color: #058377; font-family: Google Sans; sans-serif; color: white"
  );


$(function() {
    $('#terminal').terminal([
       {

       },
       function(command) {
           if(command === 'help'){
               this.echo("Available commands: help, credits, clear, github, or type a phlang command");
           } else if(command === 'credits'){
                this.echo("WebPH - A web-based pHLang interpreter");
                this.echo("Copyright (C) 2022 Henry Martin");
                this.echo("This program comes with ABSOLUTELY NO WARRANTY. ");
                this.echo("This is free software, and you are welcome to redistribute it");
                this.echo("under certain conditions; see the LICENSE file for details.");
            } else if(command === 'clear'){
                this.clear();
                console.clear();
                console.log(
                    "%c webPH %c v0.0.1 alpha",
                    "border-radius: 3px 0px 0px 3px; padding: 1%; font-size:1.3em; font-weight: 500; background-color: #00796A; font-family: Google Sans; sans-serif; color: white",
                    "border-radius: 0px 3px 3px 0px; padding: 1%; font-size:1.3em; font-weight: 400; background-color: #058377; font-family: Google Sans; sans-serif; color: white"
                  );
            } else if(command === 'github'){
                this.echo("https://github.com/HENRYMARTIN5/PhLang/tree/master/webph");
            } else {
                this.echo(pheval(command));
            }
       }
    ]);
    $("#terminal").terminal().clear();
    $("#terminal").terminal().echo("Welcome to WebPH! Type help for a list of commands.");
 });