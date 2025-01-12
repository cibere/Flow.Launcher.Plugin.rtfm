function removeItemFromArray(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
      arr.splice(index, 1);
    }
    return arr;
}
function containsObject(obj, list) {
    var i;
    for (i = 0; i < list.length; i++) {
        if (list[i] === obj) {
            return true;
        }
    }

    return false;
}

// region Library Table

function deleteRow(button) {
    console.log(button)
    console.log(button.onclick)
    let td = button.parentNode;
    console.log("td", td)
    let row = td.parentNode;
    console.log("row", row)
    row.remove();
}

function addLibrary(library) {
    let name = library['name'];
    let location = library['loc'];
    let type = library['type'];
    console.log("Adding library", library)

    let table_parent = document.getElementById("table");
    let table = table_parent.children[0];
    let row = document.createElement("tr");
    row.className = "library";

    // Edit Column

    let editTd = document.createElement("td");
    editTd.className = "center w2";
    let editBtn = document.createElement("button");
    editBtn.className = "edit-btn";
    editBtn.innerText = "edit";
    editBtn.onclick = function() {editLibraryModal(library)};
    editTd.appendChild(editBtn);
    row.appendChild(editTd);

    // Name Column

    let keywordTd = document.createElement("td");
    keywordTd.className = "content-td w15";
    keywordTd.innerText = name;
    row.appendChild(keywordTd);

    // Type Column

    let typeTd = document.createElement("td");
    typeTd.className = "content-td w15";
    typeTd.innerText = type;
    row.appendChild(typeTd);

    // Location Column

    let urlTd = document.createElement("td");
    urlTd.className = "content-td";
    if (!(location === null)){
        urlTd.innerText = location
    }
    row.appendChild(urlTd);

    table.appendChild(row);
}

function refreshTable(){
    let rows = document.getElementsByClassName("library");
    while (rows.length > 0) {
        rows[0].remove();
    }
    for (let lib of libraries){
        addLibrary(lib);
    }
}

document.addEventListener('DOMContentLoaded', refreshTable)

function createModal(){
    let modal = document.createElement("div");
    modal.className = "modal";

    let contentContainer = document.createElement("div");
    contentContainer.className = "modal-content";
    modal.appendChild(contentContainer);

    let closeBtn = document.createElement("span");
    closeBtn.className = "close";
    closeBtn.innerText = "x";
    closeBtn.onclick = function() {
        modal.remove();
    };
    contentContainer.appendChild(closeBtn);

    document.body.insertBefore(modal, document.body.firstChild);
    return contentContainer;
}

// region Add Lib Modal

function createLibraryModal(){
    let modal = createModal();
    
    let nameEl = document.createElement("input");
    nameEl.id = "create-modal-name-el";
    let nameLabel = document.createElement("label");
    nameLabel.for = "create-modal-name-el";
    nameLabel.innerText = "Manual Name (this is the keyword you will use to query it): "
    modal.appendChild(nameLabel);
    modal.appendChild(nameEl);

    modal.appendChild(document.createElement("br"));
    modal.appendChild(document.createElement("br"));

    let urlEl = document.createElement("input");
    urlEl.id = "create-modal-url-el";
    let urlLabel = document.createElement("label");
    urlLabel.for = "create-modal-url-el";
    urlLabel.innerText = "Manual Url (ensure its the root of the manual version): "
    modal.appendChild(urlLabel);
    modal.appendChild(urlEl);

    let createBtn = document.createElement("button");
    createBtn.innerText = "Create";
    createBtn.onclick = async function(){
        let lib = await getLibraryFromUrl(nameEl.value, urlEl.value);
        if (lib){
            libraries.push(lib);
            refreshTable();
            modal.parentNode.remove();
        }
    }
    modal.appendChild(createBtn);
}

// region Edit Lib Modal

function _createTextareaInput(label, def, id, disabled=false){
    let container = document.createElement("div");

    let labelEl = document.createElement("label");
    labelEl.for = id;
    labelEl.innerText = label;
    container.appendChild(labelEl);

    let textarea = document.createElement("textarea");
    textarea.id = id;
    textarea.value = def;
    if (disabled === true){
        textarea.className = "disabled";
        textarea.disabled = disabled;
    }
    container.appendChild(textarea);

    return textarea;
}

function _createCheckboxInput(label, def, id, disabled){
    let container = document.createElement("div");

    let labelEl = document.createElement("label");
    labelEl.for = id;
    labelEl.innerText = label;
    container.appendChild(labelEl);

    let inp = document.createElement("input");
    inp.type = "checkbox";
    inp.id = id;
    inp.checked = def;
    container.appendChild(inp);

    if (disabled === true){
        inp.disabled = disabled;
        inp.className = "disabled";
        let infoBox = document.createElement("span");
        infoBox.innerText = "This preset is marked as an API, so the useage of a cache isn't allowed.";
        infoBox.className = "small-font";
        container.appendChild(document.createElement("br"));
        container.appendChild(infoBox);
    }

    return inp;
}

function editLibraryModal(library){
    let modal = createModal();

    let nameEl = _createTextareaInput("Name: ", library['name'], "modal-lib-name-input")
    modal.appendChild(nameEl.parentNode);

    let typeEl = _createTextareaInput("Type: ", library['type'], "modal-lib-type-input", true)
    modal.appendChild(typeEl.parentNode);

    let locEl = _createTextareaInput("Location: ", library.loc, "modal-lib-loc-input", true)
    modal.appendChild(locEl.parentNode);

    let cacheEl = _createCheckboxInput("Use Cache: ", library['use_cache'], "modal-lib-cache-input", library['is_api'])
    modal.appendChild(cacheEl.parentNode);

    let hr = document.createElement("hr");
    modal.appendChild(hr);

    let saveBtn = document.createElement("button");
    saveBtn.className = "saveBtn button";
    let saveBtnTxt = document.createElement("span");
    saveBtnTxt.innerText = "Save";
    saveBtn.appendChild(saveBtnTxt);
    saveBtn.onclick = function(){
        library['name'] = nameEl.value;
        library['use_cache'] = cacheEl.checked;
        if (!containsObject(library, libraries)){
            libraries.push(library);
        }
        refreshTable();
        modal.parentNode.remove();
    }
    modal.appendChild(saveBtn);

    let delBtn = document.createElement("button");
    delBtn.className = "delBtn button";
    let delBtnTxt = document.createElement("span");
    delBtnTxt.innerText = "Delete";
    delBtn.appendChild(delBtnTxt);
    delBtn.onclick = function(){
        console.log("prompting for delete")
        let sure = prompt("Are you sure? Type 'yes' to confirm.")
        if (sure === 'yes'){
            removeItemFromArray(libraries, library);
            refreshTable();
            modal.parentNode.remove();
        } else {
            alert("Cancelling deletion");
        }
    }

    modal.appendChild(delBtn);
}

// region API Functions

async function saveSettings() {
    let staticPortEl = document.getElementById("static-port");
    let settingsKeywordEl = document.getElementById("settings-keyword");
    let payload = {
        port: Number(staticPortEl.value),
        keyword: settingsKeywordEl.value,
        libraries: libraries
    }
    console.log("Data for new settings", payload)

    let resp = await fetch("/api/settings", {
        method: "PUT",
        body: JSON.stringify(payload)
    }).then(response => response.json())
    console.log("Got settings response", resp)
    if (resp.success){
        console.log("Saved settings response", resp);
        alert("Settings successfully saved")
    } else {
        alert(`An error occured: ${resp.message}`)
    }
}
async function getLibraryFromUrl(name, url) {
    let payload = {
        url: url,
        name: name
    }
    console.log("Data for getting library", payload);

    let resp = await fetch("/api/get_library", {
        method: "POST",
        body: JSON.stringify(payload)
    }).then(response => response.json())
    console.log("Got get library response", resp)
    if (resp.success){
        return resp.data;
    } else {
        console.log(resp.message);
        alert(resp.message);
    }
}
async function importSettings(code) {
    payload = {
        data: code
    }
    let resp = await fetch("/api/import_settings", {
        method: "POST",
        body: JSON.stringify(payload)
    }).then(response => response.json())
    console.log("Got import settings response", resp)
    if (resp['success'] === true){
        console.log("Settings Imported", resp);
        alert("Settings have been imported. Restart flow for them to fully take affect.");
    } else {
        console.log("Data was malformed and settings were not imported successfully.", resp);
        alert("Data was malformed and settings were not imported successfully. Restart flow launcher for port setting to take affect.");
    }
    
}
async function exportSettings() {
    let resp = await fetch("/api/export_settings", {
        method: "GET"
    }).then(response => response.json())
    console.log("Got export settings response", resp)
    navigator.clipboard.writeText(resp['data'])
    console.log("Settings exported", resp);
    alert("Settings have been successfully exported. You can use the text that has been copied to your clipboard to import them on another device.");
}