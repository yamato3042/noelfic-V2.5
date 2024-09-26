
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