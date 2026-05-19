
function openDeleteModal(id, titre) {
    // Remplir le titre dans la modale
    document.getElementById('deleteEmploiTitre').textContent = titre;
    
    // Modifier l'action du formulaire
    var deleteUrl = "{% url 'emploidutemps:emploi_supprimer' 0 %}".replace('0', id);
    document.getElementById('deleteForm').action = deleteUrl;
    
    // Afficher la modale
    document.getElementById('deleteModal').style.display = 'flex';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
}

// Fermer la modale avec la touche Echap
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeDeleteModal();
    }
});

// Fermer la modale en cliquant sur l'overlay
document.getElementById('deleteModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        closeDeleteModal();
    }
});
