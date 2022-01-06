window.hasLoaded = false;
const timeout = setTimeout(evalAllPhlang, 100);

function evalAllPhlang(){
    if(window.hasLoaded){
        for(node in document.getElementsByTagName("script")){
            tag = document.getElementsByTagName("script")[node];
            if(tag.type == "text/phlang"){
                if(!tag.src){
                    var code = tag.innerHTML;
                    pheval(code);
                } else {
                    fetch(tag.src).then(text => pheval(text));
                }
                
            }
        }
        clearTimeout(timeout);
    } else {
        return;
    }
}

