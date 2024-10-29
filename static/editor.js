function emotdic() {
    var map = new Map;
    map.set(":):", "1");
    map.set(":question:", "2");
    map.set(":g)", "3");
    map.set(":d)", "4");
    map.set(":cd:", "5");
    map.set(":monde:", "6");
    map.set(":p)", "7");
    map.set(":malade:", "8");
    map.set(":pacg:", "9");
    map.set(":pacd:", "10");

    map.set(":noel:", "11");
    map.set(":o))", "12");
    map.set(":snif2:", "13");
    map.set(":-(", "14");
    map.set(":-((", "15");
    map.set("apple", "16");
    map.set(":gba:", "17");
    map.set(":hap:", "18");
    map.set(":nah:", "19");
    map.set(":snif:", "20");

    map.set(":mort:", "21");
    map.set(":ouch:", "22");
    map.set(":-)))", "23");
    map.set(":content:", "24");
    map.set(":nonnon:", "25");
    map.set(":cool:", "26");
    map.set(":sleep:", "27");
    map.set(":doute:", "28");
    map.set(":hello:", "29");
    map.set(":honte:", "30");

    map.set(":-p", "31");
    map.set(":lol:", "32");
    map.set(":non2:", "33");
    map.set(":monoeil:", "34");
    map.set(":non:", "35");
    map.set(":ok:", "36");
    map.set(":oui:", "37");
    map.set(":rechercher:", "38");
    map.set(":rire:", "39");
    map.set(":-D", "40");

    map.set(":rire2:", "41");
    map.set(":salut:", "42");
    map.set(":sarcastic:", "43");
    map.set(":up:", "44");
    map.set(":(", "45");
    map.set(":-)", "46");
    map.set(":peur:", "47");
    map.set(":bye:", "48");
    map.set(":dpdr:", "49");
    map.set(":fou:", "50");

    map.set(":gne:", "51");
    map.set(":dehors:", "52");
    map.set(":fier:", "53");
    map.set(":coeur:", "54");
    map.set(":rouge:", "55");
    map.set(":sors:", "56");
    map.set(":ouch2:", "57");
    map.set(":merci:", "58");
    map.set(":svp:", "59");
    map.set(":ange:", "60");

    map.set(":diable:", "61");
    map.set(":gni:", "62");
    map.set(":spoiler:", "63");
    map.set(":hs:", "64");
    map.set(":desole:", "65");
    map.set(":fete:", "66");
    map.set(":sournois", "67");
    map.set(":hum:", "68");
    map.set(":bravo:", "69");
    map.set(":banzai:", "70");

    map.set(":bave:", "71");
    map.set(":cimer:", "72");
    map.set(":ddb:", "73");
    map.set(":cute:", "74");
    map.set(":objection:", "75");
    map.set(":pave:", "76");
    map.set(":pf:", "77");
    map.set(":play:", "78");
    map.set(":siffle:", "79");
    return map;
}


const toolbarOptions = [
    ['bold', 'italic', 'underline'], // Boutons de formatage de texte
    [{ 'align': ['', 'center', 'right'] }], // Boutons d'alignement
    ['image'], // Bouton pour insérer une image
];


const quill = new Quill('#editor', {
    theme: 'snow',

    modules: {
        toolbar: toolbarOptions
    }
});

var toolbar = quill.getModule('toolbar');
toolbar.addHandler('image', function () {
    var range = quill.getSelection();
    if (range) {
        var url = prompt('Veuillez entrer l\'URL de l\'image : ');
        if (url) {
            quill.insertEmbed(range.index, 'image', url, 'user');
        }
    }
});



// Ajouter un bouton personnalisé pour les émoticônes
function emoticonButton_click() {
    let emot_selector = document.getElementById("emot_selector")
    if (emot_selector.style.display == 'none') {
        emot_selector.style.display = 'flex'
    } else {
        emot_selector.style.display = 'none'
    }
}
var emoticonButton = document.createElement('button');
emoticonButton.classList.add('ql-emoticon', 'fas', 'fa-smile');
emoticonButton.id = "emotButton"
emoticonButton.addEventListener('click', function () {
    emoticonButton_click()
});



// Ajouter le bouton personnalisé à la barre d'outils
var toolbarContainer = document.querySelector('.ql-toolbar');
toolbarContainer.appendChild(emoticonButton);

function insert_emot(val) {
    console.log(val)
    var selection = quill.getSelection(true);
    quill.insertText(selection.index, val)

    if(document.getElementById("preview_emot_checkbox").checked) {avec_previsu()}
}

function update_previsu() {
    //On met à jour le si on prévisualise les emots ou pas en fonction de la checkbox
    let checked = document.getElementById("preview_emot_checkbox").checked
    if(checked) {
        avec_previsu()
    }
    else {
        sans_previsu()
    }
}

function sans_previsu() {
    //Sans previsu, les emots sont en :emots: 
    let dic = emotdic()
    let content = quill.root.innerHTML
    for (let [key, value] of dic) {
        let cur = '<img src="/static/emots/' + value + '.gif">'
        content = content.replaceAll(cur, key)
    }
    quill.root.innerHTML = content  
}

function avec_previsu() {
    //Avec previsu, on a les images à la place
    let dic = emotdic()
    let content = quill.root.innerHTML
    for (let [key, value] of dic) {
        let cur = "<img src='/static/emots/" + value + ".gif'>"
        content = content.replaceAll(key, cur)
    }
    quill.root.innerHTML = content
}

//On remplis l'element
function generate_emot_selector() {
    console.log("Generate")
    //On prend les clés du dictionnaire et on fait un innerhtml
    let content = ""
    let dic = emotdic()
    console.log(dic)

    for (let [key, value] of dic) {
        let cur = "<img src='/static/emots/" + value + ".gif' onclick='insert_emot(\"" + key + "\")'/>"
        content += cur
    }
    content += "<div><input type='checkbox' id='preview_emot_checkbox' name='preview_emot_checkbox' onchange='update_previsu()'/><label for='preview_emot_checkbox'>Prévisualiser</label></div>"
    document.getElementById("emot_selector").innerHTML = content
}

generate_emot_selector()
emoticonButton_click()