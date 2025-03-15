// Description: Override de standaard Django functie showRelatedObjectPopup
//              om een pop-up venster te openen met een aangepaste vorm.
//              De functie showMyAdminPopup wordt aangeroepen wanneer een
//              link wordt aangeklikt die een pop-up venster opent. De
//              functie bepaalt de grootte en positie van het venster en
//              opent het venster met de juiste afmetingen en positie.
//              De functie addPopupIndex voegt een index toe aan de naam
//              van het venster om te voorkomen dat er meerdere vensters
//              met dezelfde naam worden geopend. De functie setPopupIndex 
//              bepaalt de index van het venster op basis van de naam van
//              het venster. De functie showRelatedObjectPopup wordt
//              overschreven om de aangepaste functie showMyAdminPopup
//              aan te roepen wanneer een link wordt aangeklikt die een
//              pop-up venster opent.


function addPopupIndex(name) {
    // Voeg een index toe aan de naam van het venster
    // Overide van de functie in RelatedObjectLookups.js
    name = name + "__" + (popupIndex + 1);
    return name;
}

function setPopupIndex() {
    // Bepaal de index van het venster
    // Overide van de functie in RelatedObjectLookups.js
    if(document.getElementsByName("_popup").length > 0) {
        const index = window.name.lastIndexOf("__") + 2;
        popupIndex = parseInt(window.name.substring(index));   
    } else {
        popupIndex = 0;
    }
}


function showMyAdminPopup(triggeringLink, name_regexp, add_popup) {
    // Open een pop-up venster met aangepaste afmetingen en positie
    // Overide van de functie in RelatedObjectLookups.js
    setPopupIndex();
    const name = addPopupIndex(triggeringLink.id.replace(name_regexp, ''));
    const href = new URL(triggeringLink.href);
    
    if (add_popup) {
        href.searchParams.set('_popup', 1);
    }

    // Afmetingen van het pop-up venster
    const popupWidth = 800;
    const popupHeight = 800;

    // Bereken het midden van het scherm
    const screenWidth = window.innerWidth || screen.width;
    const screenHeight = window.innerHeight || screen.height;
    const left = (screenWidth - popupWidth) / 2;
    const top = (screenHeight - popupHeight) / 2;
    window.myWin = window.open(
        href, 
        name, 
        `left=${left},top=${top},height=${popupHeight},width=${popupWidth},resizable=yes,scrollbars=yes`
    );
    
    window.myWin.focus();
    return false;
}


// Override de standaard Django functie
window.showRelatedObjectPopup = function(triggeringLink) {
    // Open een pop-up venster met aangepaste afmetingen en positie

    return showMyAdminPopup(triggeringLink, /^(change|add|delete)_/, false);
};
