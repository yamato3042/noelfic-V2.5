//Ce script vas contenir toutes les fonctions pour manipuler le système d'édition de fic
function select_add_element(select, value, text) {
    //Cette fonction vas en gros rajouter un élement dans une select
    let optionElement = document.createElement('option');
    optionElement.value = value
    optionElement.textContent = text
    select.appendChild(optionElement);
}
function select_clean(select) {
    //Cette fonction vas en gros nettoyer un select
    select.innerHTML = ""
}
async function fetch_val(adress, param = {}, retType="json") {
    //Cette fonction vas fetch sur le serveur un JSON
    const formData = new FormData();
    formData.append("token", temp_token);

    //On ajoute les valeurs de param
    for (const [clé, valeur] of Object.entries(param)) {
        console.log(`Clé: ${clé}, Valeur: ${valeur}`);
        formData.append(clé, valeur)
    }

    const response = await fetch("/comptes/edit_fics/" + adress, {
        method: "POST",
        body: formData,
    })

    if(retType=="json") {
        return await response.json()
    }
    else if(retType=="text") {
        return await response.text()
    }

}

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
        const fics = await fetch_val("getFics")

        let select = document.getElementById("fic_select");
        select_clean(select)

        select_add_element(select, -1, "-----")

        fics.forEach(element => {
            select_add_element(select, element["id"], element["titre"])
        });
    }

    fic_select_onchange() {
        //Lorsque l'élement courant de fic_select change
        console.log("fic select change")
        this.get_collaborateurs()
    }
    fic_select_new() {
        //Permet de créer une nouvelle fic
    }

    async get_collaborateurs() {
        let fic = document.getElementById("fic_select").value
        let collaborateurs = await fetch_val("collaborateur_select", {"fic" : fic});
        console.log(collaborateurs)
        //On affiche les valeurs
        let select = document.getElementById("perso_colab_select")
        select_clean(select)
        select_add_element(select, -1, "-----")

        collaborateurs.forEach(element => {
            select_add_element(select, element["id"], element["name"])
            if(element["type"] == "current") {this.collaborateurs_current = element["id"]}
            else if(element["type"] == "proprio") {this.collaborateurs_proprio = element["id"]}
        });
    }

    add_collaborateurs() {
    }

    async remove_collaborateurs() {
        //On est pas censé pour s'enlever ou enlever le proprio de la fic
        let select = document.getElementById("perso_colab_select")

        if(select.value == this.collaborateurs_proprio || select.value == this.collaborateurs_current) {
            alert("Action impossible")
            return
        }

        let fic = document.getElementById("fic_select").value

        let ret = await fetch_val("collaborateur_delete", {"fic" : fic, "toremove": select.value}, "text");
        console.log(ret)

        if(ret == "OK") {
            this.get_collaborateurs()
        } else {
            alert("Erreur")
        }

    }

    cacheur(val) {
        //Cette fonction a pour but de cacher les élements si la partie a pas encore été chargé
    }
}

let fic_editor = new Fic_editor()
console.log("fic_editor")
fic_editor.fic_select_fetch()