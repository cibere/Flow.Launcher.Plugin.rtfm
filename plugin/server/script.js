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

// region Add Lib Modal

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

function makeSelectInput(label, options, id, nextModalGen){
    let container = document.createElement("div");

    let labelEl = document.createElement("label");
    labelEl.for = id;
    labelEl.innerText = label;
    container.appendChild(labelEl);

    let menu = document.createElement("select");
    menu.id = id;
    for (let text of options){
        let opt = document.createElement("option");
        opt.innerText = text;
        menu.appendChild(opt);
    }
    container.appendChild(menu);

    let nextBtn = document.createElement("button");
    nextBtn.innerText = "Add";
    nextBtn.onclick = function(){
        container.parentNode.parentNode.remove();
        nextModalGen(menu.options[menu.selectedIndex].innerText);
    }
    container.appendChild(nextBtn)

    return container;
}

function _makePresetInput(){
    return makeSelectInput("Select a preset: ", presetOptions, "modal-select-preset-docs", function(value){
        libraries.push(
            {
                name:prompt("What should the name be? This will be used as the keyword you will use to access the documentation."),
                type:`${value}`,
                loc:null,
                use_cache:true
            }
        );
        refreshTable();
    })
}

function _makeTypeInput(){
    return makeSelectInput("Select a doctype: ", docTypes, "modal-select-doctype", function(value){
        let lib = {
            name:"",
            type:value,
            loc:"",
            use_cache:true
        }
        editLibraryModal(lib);
    })
}

function createLibraryModal(){
    let modal = createModal();
    modal.appendChild(_makePresetInput());

    let orEl = document.createElement("p");
    orEl.innerText = "or";
    modal.appendChild(orEl);

    modal.appendChild(_makeTypeInput());
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

function _createCheckboxInput(label, def, id){
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

    return inp;
}

function editLibraryModal(library){
    let modal = createModal();

    let nameEl = _createTextareaInput("Name: ", library['name'], "modal-lib-name-input")
    modal.appendChild(nameEl.parentNode);

    let typeEl = _createTextareaInput("Type: ", library['type'], "modal-lib-type-input", true)
    modal.appendChild(typeEl.parentNode);

    if (library['loc'] === null){
        var opts = [null, true]
    } else {
        var opts = [library['loc'], false]
    }

    let locEl = _createTextareaInput("Location: ", opts[0], "modal-lib-loc-input", opts[1])
    modal.appendChild(locEl.parentNode);

    let cacheEl = _createCheckboxInput("Use Cache: ", library['use_cache'], "modal-lib-cache-input")
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
        library['type'] = typeEl.value;
        if (opts[1] === false){
            library['loc'] = locEl.value;
        }
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
    console.log("Data for new settings", libraries)

    let resp = await fetch("/api/save_settings", {
        method: "PUT",
        body: JSON.stringify(libraries)
    }).then(response => response.json())
    console.log("Saved settings response", resp);
    alert("Settings successfully saved")
}
async function setSettingsKeyword() {
    let el = document.getElementById("settings-keyword");
    let data = {
    keyword: el.value
    }
    let resp = await fetch("/api/set_main_kw", {
        method: "PUT",
        body: JSON.stringify(data)
    }).then(response => response.json())
    
    console.log("Settings Keyword Saved", resp);
    alert("Settings Keyword Successfully Updated")
}