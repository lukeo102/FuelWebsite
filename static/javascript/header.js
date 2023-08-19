const nav = document.querySelector('nav');
var nav_show = false

function toggleNav() {
    if (nav_show) {
        nav.style.display = "none"
    } else {
        nav.style.display = "block"
    }
    nav_show = ! nav_show
}