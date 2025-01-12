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
 * @property {boolean} use_cache
 * @property {boolean} is_api
 */

/** @typedef {ServerResponse<GetLibraryResponseData>} GetLibraryResponse */

/** @typedef {ServerResponse<undefined>} SettingsResponse */

const elements = {
    /** @type {HTMLTemplateElement} */
    template: document.querySelector("#docs-template"),
    /** @type {HTMLFormElement} */
    mainForm: document.querySelector("#main-form"),
    /** @type {HTMLFormElement} */
    addManualForm: document.querySelector("#add-manual-form"),
    /** @type {HTMLButtonElement} */
    addManualButton: document.querySelector("#add-manual-btn"),
    /** @type {HTMLInputElement} */
    addManualKeyword: document.querySelector("#add-manual-keyword"),
    /** @type {HTMLInputElement} */
    addManualLoc: document.querySelector("#add-manual-loc"),
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

    const useCacheInput = card.querySelector('input[name$="use_cache"]');
    useCacheInput.checked = data.use_cache;
    useCacheInput.disabled = data.is_api;

    const isApiInput = card.querySelector('input[name$="is_api"]');
    isApiInput.checked = data.is_api;

    elements.mainForm.appendChild(doc);
}

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
        alert(`An error occurred: ${response.message}`);
        return;
    }

    alert("Success!");
});

elements.addManualForm.addEventListener("submit", async e => {
    e.preventDefault();

    const location = elements.addManualLoc.value;
    const keyword = elements.addManualKeyword.value;

    const payload = {
        url: location,
        name: keyword,
    };
    /** @type {GetLibraryResponse} */
    const response = await fetch(elements.addManualForm.action, {
        method: elements.addManualForm.method ?? "POST",
        body: JSON.stringify(payload),
    }).then(v => v.json());
    console.log("Got get library response", response);

    if (!response.success) {
        alert(`An error occurred: ${response.message}`);
        return;
    }

    alert("Success!");
    addNewDoc(response.data);
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