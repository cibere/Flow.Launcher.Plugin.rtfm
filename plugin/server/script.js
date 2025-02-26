/**
 * @template T
 * @typedef {object} SuccessfulResponse
 * @property {true} success
 * @property {T} data
 */

/**
 * @typedef {object} FailedResponse
 * @property {false} success
 * @property {string} message
 */

/**
 * @template T
 * @typedef {SuccessfulResponse<T> | FailedResponse} ServerResponse
 */

/**
 * @typedef {object} GetLibraryResponseData
 * @property {string} name
 * @property {string} type
 * @property {string} loc
 * @property {boolean} dont_cache_results
 * @property {boolean} is_api
 */

/** @typedef {ServerResponse<GetLibraryResponseData>} GetLibraryResponse */

/** @typedef {ServerResponse<undefined>} SettingsResponse */

const elements = {
    /** @type {HTMLTemplateElement} */
    template: document.querySelector("#docs-template"),
    /** @type {HTMLFormElement} */
    mainForm: document.querySelector("#main-form"),
    /** @type {HTMLDivElement} */
    addManualDiv: document.querySelector("#add-manual-form"),
    /** @type {HTMLButtonElement} */
    addManualButton: document.querySelector("#add-manual-btn"),
    /** @type {HTMLInputElement} */
    addManualKeyword: document.querySelector("#add-manual-keyword"),
    /** @type {HTMLInputElement} */
    addManualLoc: document.querySelector("#add-manual-loc"),
    /** @type {HTMLDialogElement} */
    loadingModal: document.querySelector("#loading-modal"),
    /** @type {HTMLButtonElement} */
    importBtn: document.querySelector("#import-btn"),
    /** @type {HTMLButtonElement} */
    exportBtn: document.querySelector("#export-btn"),
    /** @type {HTMLDialogElement} */
    alertModal: document.querySelector("#alert-modal"),
    /** @type {HTMLDivElement} */
    alertModalContents: document.querySelector("#alert-modal-contents"),
};

/**
 * @param {GetLibraryResponseData} data
 */
function addNewDoc(data) {
    const doc = elements.template.content.cloneNode(true);
    const index = elements.mainForm.children.length;

    const card = doc.querySelector('.card');
    card.dataset.index = index.toString();
    card.innerHTML = card.innerHTML
        .replaceAll("{{INDEX}}", index)
        .replaceAll("{{LOCATION}}", data.loc)
        .replaceAll("{{NAME}}", data.name)
        .replaceAll("{{TYPE}}", data.type);

    const useCacheInput = card.querySelector('input[name$="dont_cache_results"]');
    useCacheInput.checked = !data.options.dont_cache_results;

    const isApiInput = card.querySelector('input[name$="is_api"]');
    isApiInput.checked = data.options.is_api;

    elements.addManualDiv.insertAdjacentElement("afterend", doc.querySelector(".card"));

    elements.addManualDiv.querySelectorAll("input").forEach(inp => {
        inp.value = "";
    })
}

function showLoadingModal() {
    elements.loadingModal.showModal();
}

function hideLoadingModal() {
    elements.loadingModal.close();
}

let resolveAlertModal;

function showAlertModal(msg){
    if (resolveAlertModal) {
        resolveAlertModal();
        resolveAlertModal = null;
    }
    elements.alertModalContents.innerHTML = msg;
    elements.alertModal.showModal();
    return new Promise(resolve => resolveAlertModal = resolve);
}

elements.alertModal.addEventListener("click", async e => {
    elements.alertModal.close();
    if (resolveAlertModal) {
        resolveAlertModal();
        resolveAlertModal = null;
    }
})

elements.mainForm.addEventListener("submit", async e => {
    e.preventDefault();

    const formData = new FormData(elements.mainForm);

    const payload = Object.fromEntries(formData.entries());

    /** @type {SettingsResponse} */
    const response = await fetch(elements.mainForm.action, {
        method: elements.mainForm.method ?? "POST",
        body: JSON.stringify(payload),
    }).then(v => v.json());
    console.log("Got settings response", response);

    if (!response.success) {
        console.log("Saved settings response", response);
        showErrorModal(`An error occurred: ${response.message}`);
        return;
    }

    showAlertModal("Success!");
});

elements.addManualButton.addEventListener("click", async () => {
    console.log('clicked');
    try {
        showLoadingModal();
        const location = elements.addManualLoc.value;
        const keyword = elements.addManualKeyword.value;

        const payload = {
            url: location,
            name: keyword,
        };
        console.log(elements.addManualDiv.dataset.action);
        /** @type {GetLibraryResponse} */
        const response = await fetch(elements.addManualDiv.dataset.action, {
            method: elements.addManualDiv.dataset.method ?? "POST",
            body: JSON.stringify(payload),
        }).then(v => v.json());
        console.log("Got get library response", response);

        hideLoadingModal();
        if (!response.success) {
            showAlertModal(`An error occurred: ${response.message}`);
            return;
        }

        showAlertModal("Success!");
        addNewDoc(response.data);
    } catch (e) {
        hideLoadingModal();
    }
});

/**
 * @param {HTMLElement} parent
 * @param {string} selector
 * @param {string} attrName
 * @param {number} newIndex
 * @returns {void}
 */
function replaceIndexInAttribute(parent, selector, attrName, newIndex) {
    const elements = parent.querySelectorAll(selector);
    for (const element of elements) {
        const attrValue = element.getAttribute(attrName);
        if (!attrValue) continue;
        const newValue = attrValue
            .replace(/\.\d+\./, `.${newIndex}.`)
            .replace(/-\d+$/, `-${newIndex}`);
        element.setAttribute(attrName, newValue);
    }
}

elements.mainForm.addEventListener("click", e => {
    if (!e.target.classList.contains("remove-btn")) return;

    e.target.closest(".card")?.remove();

    /** @type {NodeListOf<HTMLDivElement>} */
    const allCards = elements.mainForm.querySelectorAll(".card");
    for (let i = 0; i < allCards.length; i++) {
        const card = allCards[i];
        if (card.dataset.index === i.toString()) continue;
        card.dataset.index = i.toString();
        replaceIndexInAttribute(card, `label`, 'for', i);
        replaceIndexInAttribute(card, `input`, 'id', i);
        replaceIndexInAttribute(card, `input`, 'name', i);
    }
});

elements.importBtn.addEventListener("click", () => {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".txt";
    fileInput.click();
    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];
        const reader = new FileReader();
        reader.readAsText(file);
        reader.addEventListener("load", async () => {
            const data = reader.result;
            try {
                let response = await fetch("/api/settings/import", {
                    body: JSON.stringify({data}),
                    method: "POST",
                }).then(v => v.json());
                if (!response.success) {
                    return showAlertModal("Failed to import settings");
                }
                console.log("Got Response from import settings endpoint", response);
                await showAlertModal("Settings imported successfully! A full restart of flow launcher is needed for all new settings to take affect.");
                window.location.reload();
            } catch {
                showAlertModal("Failed to import settings!");
            }
        });
    });
});

elements.exportBtn.addEventListener("click", async () => {
    try {
        const data = await fetch("/api/settings/export").then(res => res.json());
        if (!data.success) {
            showAlertModal("Failed to export settings!");
            return;
        }
        const file = new Blob([data.data], {type: "text/plain"});
        const url = URL.createObjectURL(file);
        const a = document.createElement("a");
        a.href = url;
        a.download = "rtfm_settings.txt";
        a.click();
        URL.revokeObjectURL(url);
        showAlertModal("Settings exported successfully!");
        location.reload();
    } catch {
        showAlertModal("Failed to export settings!");
    }
});