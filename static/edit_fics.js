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
async function fetch_val(adress, param = {}, retType = "json") {
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

    if (retType == "json") {
        return await response.json()
    }
    else if (retType == "text") {
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
        if (document.getElementById("fic_select").value == '-1') {
            this.cacheur(1)
        } else {
            //Lorsque l'élement courant de fic_select change
            console.log("fic select change")
            this.get_collaborateurs()
            this.get_personalisation()
            this.cacheur(2)
        }
    }
    async fic_select_new() {
        //Permet de créer une nouvelle fic
        let ficname = prompt("Veuillez choisir un titre pour cette nouvelle fic")
        if (ficname != "") {
            //On fait la requête
            let val = await fetch_val("fic_create", { "title": ficname }, "text");
            console.log(val)
            if (val == "ERR_ALREADY_EXIST") {
                alert("La fic existe déjà")
            } else if (parseInt(val) != NaN) {
                alert("La fic a été créé avec succès")
                await this.fic_select_fetch()
                document.getElementById("fic_select").value = val
                this.fic_select_onchange()
            }
        }
    }

    async get_collaborateurs() {
        let fic = document.getElementById("fic_select").value
        let collaborateurs = await fetch_val("collaborateur_select", { "fic": fic });
        //On affiche les valeurs
        let select = document.getElementById("perso_colab_select")
        select_clean(select)
        select_add_element(select, -1, "-----")

        collaborateurs.forEach(element => {
            select_add_element(select, element["id"], element["name"])
            if (element["type"] == "current") { this.collaborateurs_current = element["id"] }
            else if (element["type"] == "proprio") { this.collaborateurs_proprio = element["id"] }
        });

        //On met à jour le bordel pour l'auteur des chapitres
        let select_auteur_chap = document.getElementById("content_auteur")
        let ancienne_val = select_auteur_chap.value

        select_clean(select_auteur_chap)
        collaborateurs.forEach(element => {
            select_add_element(select_auteur_chap, element["id"], element["name"])
        });
        if (ancienne_val >= 1) {
            select_auteur_chap.value = ancienne_val;
        }
    }

    async add_collaborateurs() {
        //Petit message pour demander le nom du collaborateur
        let username = prompt("Veuillez entrer le pseudo de l'utilisateur")
        if (username == "") {
            alert("Veuillez entrer une valeur valide.")
            return
        }
        //On fait la requête
        let fic = document.getElementById("fic_select").value
        let ret = await fetch_val("collaborateur_add", { "fic": fic, "user": username }, "text");

        if (ret == "OK") {
            this.get_collaborateurs()
        } else if (ret == "ERR_INVALID_USER") {
            alert("Utilisateur invalide.")

        } else if (ret == "ERR_ALREADY_USER") {
            alert("L'utilisateur est déjà là.")
        } else {
            alert("Erreur")
        }
    }

    async remove_collaborateurs() {
        //On est pas censé pour s'enlever ou enlever le proprio de la fic
        let select = document.getElementById("perso_colab_select")

        if (select.value == this.collaborateurs_proprio || select.value == this.collaborateurs_current) {
            alert("Action impossible")
            return
        }

        let fic = document.getElementById("fic_select").value

        let ret = await fetch_val("collaborateur_delete", { "fic": fic, "toremove": select.value }, "text");
        console.log(ret)

        if (ret == "OK") {
            this.get_collaborateurs()
        } else {
            alert("Erreur")
        }

    }


    async get_personalisation() {
        let fic = document.getElementById("fic_select").value
        let val = await fetch_val("personalisation_get", { "fic": fic })

        console.log(val)

        document.getElementById("perso_fic_titre").value = val["titre"]
        document.getElementById("perso_fic_status").value = val["status"]
        document.getElementById("perso_fic_lien").value = val["lien"]
        choices.removeActiveItems()
        choices.setChoiceByValue(val["tags"]);
        document.getElementById("perso_fic_description").value = val["description"]

        //Maintenant on s'occuppe du truc des chapitres
        let select = document.getElementById("chap_select")
        select_clean(select)
        select_add_element(select, -1, "----")
        //Maintenant on ajoute
        for (let i = 1; i <= val["nbchapitres"]; i++) {
            select_add_element(select, i, i)
        }
        select_add_element(select, 0, (val["nbchapitres"] + 1) + " (+)")
    }

    async save_personalisation() {
        let fic = document.getElementById("fic_select").value

        let valeur = { //Je vais mettre les valeurs en JSON ce sera moins chiant pour le multipart machin
            "titre": document.getElementById("perso_fic_titre").value,
            "status": document.getElementById("perso_fic_status").value,
            "lien": document.getElementById("perso_fic_lien").value,
            "tags": choices.getValue(true),
            "description": document.getElementById("perso_fic_description").value
        }
        await fetch_val("personalisation_set", { "fic": fic, "val": JSON.stringify(valeur) }, "TEXT")
    }

    async get_chapitre() {
        let fic = document.getElementById("fic_select").value
        let chapitre = document.getElementById("chap_select").value
        console.log(chapitre)

        if (chapitre == 0) {
            //Nouveau chapitre
            this.isNouveauChapitre = true;
            //Tout netoyer
            document.getElementById("content_titre").value = ""
            quill.root.innerHTML = ""
            document.getElementById("content_auteur").value = USERID

            this.cacheur(3)

        } else if (chapitre == -1) {
            //Rien
            this.isNouveauChapitre = false;
            this.cacheur(2) //TODO: La valeur elle est pas bonne hein
        } else {
            this.isNouveauChapitre = false;
            //C'est un chapitre existant, on fetch sur le serveur
            let val = await fetch_val("chapitre_get", { "fic": fic, "chapitre": chapitre })
            console.log(val)
            document.getElementById("content_titre").value = val["titre"]
            quill.root.innerHTML = val["content"]
            document.getElementById("content_auteur").value = val["auteur"]
            this.cacheur(3)
        }
    }

    async save_chapitre() {
        sans_previsu()
        //On regarde si on est sur un nouveau truc ou pas
        let fic = document.getElementById("fic_select").value
        let chapitre = document.getElementById("chap_select").value
        let titre = document.getElementById("content_titre").value
        let auteur = document.getElementById("content_auteur").value
        let content = quill.root.innerHTML

        if (chapitre > 0) {
            //On enregistre
            let val = await fetch_val("chapitre_save", { "fic": fic, "chapitre": chapitre, "titre": titre, "auteur": auteur, "content": content }, "text")
            console.log(val)
            if (val == "OK") { alert("Le chapitre a bien été sauvegardé.") }
        } else if (chapitre == 0) {
            //On crée un nouveau chapitre
            let val = await fetch_val("chapitre_create", { "fic": fic, "titre": titre, "auteur": auteur, "content": content }, "json")
            console.log(val)

            //On recharge et on met au bon numéro de chapitre
            await this.get_personalisation()
            document.getElementById("chap_select").value = val["num"]
            this.get_chapitre()
        }

    }

    cacheur(val) {
        let part_chapitre_select = document.getElementById("part_chapitre_select")
        let part_chapitre_content = document.getElementById("part_chapitre_content")
        let part_perso_fic = document.getElementById("part_perso_fic")
        console.log("cacheur : ", val)
        //Cette fonction a pour but de cacher les élements si la partie n'a pas encore été chargé
        /*L'affichage se fait en 4 étapes : 
            1 - Aucune fic n'a été sélectionné
            2 - Une fic a été sélectionné
            3 - Un chapitre a été sélectionné
        */

        part_chapitre_select.style.visibility = 'hidden'
        part_chapitre_content.style.visibility = 'hidden'
        part_perso_fic.style.visibility = 'hidden'

        if (val >= 2) {
            part_chapitre_select.style.visibility = 'visible'
            part_perso_fic.style.visibility = 'visible'
        }

        if (val == 3) {
            part_chapitre_content.style.visibility = 'visible'
        }

    }
}

let fic_editor = new Fic_editor()
console.log("fic_editor")
fic_editor.fic_select_fetch()