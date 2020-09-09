"use strict";

$(document).ready(function () {

    /* NOTE:
    If you decide to remove the fade in effect below, also remove the 'display:none' style from the #conent element in templates/base.html.
    Otherwise, you will not see the content of the page being displayed at all.
    */
    $("#content").fadeIn(750);

});

function addRow(tableID) {

    var table = document.getElementById(tableID);

    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);

    var colCount = table.rows[1].cells.length;

    for (var i = 0; i < colCount; i++) {

        var newcell = row.insertCell(i);

        newcell.innerHTML = table.rows[1].cells[i].innerHTML;
        //alert(newcell.childNodes);
        switch (newcell.childNodes[0].type) {
            case "text":
                newcell.childNodes[0].value = "";
                break;
            case "checkbox":
                newcell.childNodes[0].checked = false;
                break;
            case "select-one":
                newcell.childNodes[0].selectedIndex = 0;
                break;
        }
    }
}

function open_data(evt, table) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(table).style.display = "block";
    evt.currentTarget.className += " active";
}