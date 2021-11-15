document.addEventListener('DOMContentLoaded', function() {
    const { DateTime } = luxon;
    Array.from(document.getElementsByClassName("konvoi-date")).forEach(element => {
        let text = element.innerHTML;
        let value;

        if (text.includes(":")) {
            value = DateTime
                .fromFormat(text, "yyyy-MM-dd HH:mm:ss")
                .toFormat('dd.MM.yyyy T');
        } else {
            value = DateTime
                .fromFormat(text, "yyyy-MM-dd")
                .toFormat('dd.MM.yyyy');
        }
        
        element.innerHTML = value;
    });
});

document.addEventListener('DOMContentLoaded', function() {
    Array.from(document.getElementsByClassName("update-pic")).forEach(element => {
        new Viewer(element, {
            inline: false,
            toolbar: false,
            navbar: false,
            viewed() {
                viewer.zoomTo(1);
            },
        });
    });
});