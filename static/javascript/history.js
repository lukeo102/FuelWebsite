const history_section = document.getElementById("history-content");

function toggleVisibility(element_id, display_type) {
    element = document.getElementById(element_id);
    if (element.style.display === "none") {
        element.style.display = display_type;
    } else {
        element.style.display = "none"
    }
}

function deleteFillUp(element) {
    if (confirm("Are you sure you want to delete this fill up?")) {
        var request = new XMLHttpRequest();
        request.onreadystatechange = function() {
            if (request.readyState === 4) { // ready state 4 == DONE
                return all();
            } else { // if not done display loading bar/circle/thingy
                // loading bar
            }
        };
        request.open("GET", window.location.origin + "/history/delete_fill_up?id=" + element.value, true);
        request.send();
    }
}

function selector(selection) {
    switch(selection.value) {
        case "all":
            all();
            break;

        default:
            console.log("Nothing selected");
    }
}

function efficiency() {



}

function all() {
    var request = new XMLHttpRequest();
    request.onreadystatechange = function() {
        if (request.readyState === 4) { // ready state 4 == DONE
            let content = ``;
            console.log(request.responseText)
            data = JSON.parse(this.responseText)[0];
            console.log(data);
            for (var vehicle in data) {
                content += `<section>`;
                content += `<h2 onclick="toggleVisibility('${vehicle}', 'block')">${vehicle}</h2>`;
                content += `<section id="${vehicle}">`;
                if (data[vehicle].length === 0) {
                        content += `<h3>No fillups recorded</h3>`;
                    } else {
                    for (var i = 0; i < data[vehicle].length; i++) {

                        const date = new Date(data[vehicle][i]["date"]);
                        content += `<h3>${date.toDateString()} <button value="${data[vehicle][i]["_id"]}" onclick="deleteFillUp(this)"><img src="/static/img/x.svg" alt="Click to Delete" /></button></h3>`;
                        content += `<p>${data[vehicle][i]["amount"]} ${data[vehicle][i]["units"]} for ${data[vehicle][i]["currency"]}${data[vehicle][i]["cost"]}</p>`;
                        content += `<p>At ${data[vehicle][i]["odometer"]} ${data[vehicle][i]["odometer_units"]}</p>`;
                    }
                }

                content += `</section>`;
                content += `</section>`;
            }
            history_section.innerHTML = content;
        } else { // if not done display loading bar/circle/thingy
            // loading bar
        }
    };
    request.open("GET", window.location.origin + "/history/all", true);
    request.send();

}