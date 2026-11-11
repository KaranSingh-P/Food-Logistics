document.getElementById("hamburger").onclick = function(){
    if (document.querySelector("#menu").style.display == "none"){
        document.querySelector("#menu").style.display="flex";
    }else{
        document.querySelector("#menu").style.display="none";
    }
};

document.getElementById("showPreferencesButton").onclick = function(){
    if (document.querySelector("#generate-recipe-preferences").style.display == "none"){
        document.querySelector("#generate-recipe-preferences").style.display="block";
    }else{
        document.querySelector("#generate-recipe-preferences").style.display="none";
    }
};