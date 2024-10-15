//Ce script vas contenir toutes les fonctions pour manipuler le système d'édition de fic

class Fic_editor {
    /*
    L'édition se fait en 4 catégories :
        - fic_select, la sélection de la fiction à éditer ou la création d'une nouvelle
        - perso, la personalisation des différentes valeurs de la fic : nom, status, tags, lien externe, collaborateurs, description
        - chapitre, le numéro du chapitre à modifier, ou à défaut la création d'un nouveau
        - edit, l'édition du chapitre concerné en détail
    */
    async fic_select_fetch() {
        //Cette fonction vas récuperer les différentes fics accessibles pour l'utilisateur et les mettre dans le combobox
        const formData = new FormData();
        formData.append("token", temp_token);
        const response = await fetch("/comptes/edit_fics/getFics", {
            method: "POST",
            body: formData,
        })
        const fics = await response.json()
        console.log(fics)
        let select = document.getElementById("fic_select");

        //Le truc par défaut
        let optionElement = document.createElement('option');
        optionElement.value = -1
        optionElement.textContent = "-----"
        select.appendChild(optionElement);


        fics.forEach(element => {
            let optionElement = document.createElement('option');
            optionElement.value = element["id"];
            optionElement.textContent = element["titre"];
            select.appendChild(optionElement);
        });
    }
    fic_select_onchange() {
        //Lorsque l'élement courant de fic_select change
        console.log("fic select change")
        //TODO: Là
    }
    fic_select_new() {
        //Permet de créer une nouvelle fic
    }



    cacheur(val) {
        //Cette fonction a pour but de cacher les élements si la partie a pas encore été chargé
    }
}

let fic_editor = new Fic_editor()
console.log("fic_editor")
fic_editor.fic_select_fetch()