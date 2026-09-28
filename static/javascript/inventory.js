let currentPage = 1;
let currentPerPage = 20;


async function loadInventory(page = 1, perPage = currentPerPage) {

    try {

        const response = await fetch(
            `/api/inventory?page=${page}&per_page=${perPage}`
        );

        if (!response.ok) {
            throw new Error("Failed to fetch inventory");
        }

        const data = await response.json();

        currentPage = data.page;
        currentPerPage = data.per_page;

        renderInventory(data.items);
        renderPagination(data);

        updateURL();

    } catch (error) {

        console.error("Error loading inventory:", error);

    }
}


function renderInventory(items) {

    const tableBody = document.getElementById(
        "inventoryTableBody"
    );

    tableBody.innerHTML = "";

    items.forEach(item => {

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${item.s_no}</td>

            <td>${item.name}</td>

            <td>
                <span class="tag ${item.tag.toLowerCase()}">
                    ${item.tag}
                </span>
            </td>

            <td>${item.purchase_date}</td>

            <td>${item.expiration_date}</td>

            <td>
                <div class="action-buttons">

                    <button
                        class="edit-btn"
                        type="button"
                        data-id="${item.id}">
                        <i class="fa-solid fa-pen"></i>
                    </button>

                    <button
                        class="remove-btn"
                        type="button"
                        data-id="${item.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>

                </div>
            </td>
        `;

            const removeButton =
                row.querySelector(".remove-btn");


            removeButton.addEventListener("click", () => {
                removeItem(item.id);
            });

        tableBody.appendChild(row);
    });
}

async function removeItem(itemId) {

    try {

        const response = await fetch(
            "/api/remove-item-inventory",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    id: itemId
                })
            }
        );


        if (!response.ok) {
            throw new Error("Failed to remove item");
        }


        const result = await response.json();


        if (!result.success) {
            throw new Error(
                result.message || "Failed to remove item"
            );
        }


        // Reload current page
        loadInventory(
            currentPage,
            currentPerPage
        );


    } catch (error) {

        console.error(
            "Error removing inventory item:",
            error
        );

    }
}

function renderPagination(data) {

    const paginationTop = document.getElementById("paginationTop");
    const paginationBottom = document.getElementById("paginationBottom");

    // Clear both pagination containers
    paginationTop.innerHTML = "";
    paginationBottom.innerHTML = "";

    // Create pagination for both locations
    createPagination(paginationTop, data);
    createPagination(paginationBottom, data);
}

function createPagination(container, data) {

    const total = data.total;
    const page = data.page;
    const perPage = data.per_page;
    const totalPages = data.total_pages;


    // Summary
    const summary = document.createElement("div");

    summary.className = "pagination-summary";


    if (total === 0) {

        summary.textContent = "Showing 0–0 of 0";

    } else {

        const start = (page - 1) * perPage + 1;
        const end = Math.min(page * perPage, total);

        summary.textContent =
            `Showing ${start}–${end} of ${total}`;
    }


    container.appendChild(summary);


    // Controls
    const controls = document.createElement("div");

    controls.className = "pagination-controls";


    // Previous button
    const previousButton = document.createElement("button");

    previousButton.textContent = "‹ Previous";

    previousButton.setAttribute(
        "aria-label",
        "Previous page"
    );

    previousButton.disabled = page === 1;

    previousButton.addEventListener("click", () => {

        if (page > 1) {
            loadInventory(page - 1);
        }

    });

    controls.appendChild(previousButton);


    // Page numbers
    const pages = getPageNumbers(page, totalPages);

    pages.forEach(pageNumber => {

        if (pageNumber === "...") {

            const ellipsis = document.createElement("span");

            ellipsis.textContent = "…";

            ellipsis.setAttribute(
                "aria-hidden",
                "true"
            );

            controls.appendChild(ellipsis);

            return;
        }


        const pageButton = document.createElement("button");

        pageButton.textContent = pageNumber;


        if (pageNumber === page) {

            pageButton.setAttribute(
                "aria-current",
                "page"
            );

        }


        pageButton.addEventListener("click", () => {

            loadInventory(pageNumber);

        });


        controls.appendChild(pageButton);
    });


    // Next button
    const nextButton = document.createElement("button");

    nextButton.textContent = "Next ›";

    nextButton.setAttribute(
        "aria-label",
        "Next page"
    );

    nextButton.disabled =
        page === totalPages || totalPages === 0;


    nextButton.addEventListener("click", () => {

        if (page < totalPages) {
            loadInventory(page + 1);
        }

    });


    controls.appendChild(nextButton);


    container.appendChild(controls);


    // Page size
    const pageSizeLabel = document.createElement("label");

    pageSizeLabel.className = "page-size";


    const select = document.createElement("select");

    select.innerHTML = `
        <option value="20">20</option>
        <option value="50">50</option>
        <option value="100">100</option>
    `;


    select.value = perPage;


    select.addEventListener("change", event => {

        const newPerPage =
            parseInt(event.target.value, 10);

        currentPerPage = newPerPage;

        currentPage = 1;

        loadInventory(
            currentPage,
            currentPerPage
        );

    });


    pageSizeLabel.appendChild(select);

    pageSizeLabel.appendChild(
        document.createTextNode(" per page")
    );


    container.appendChild(pageSizeLabel);
}



function getPageNumbers(currentPage, totalPages) {

    // Small number of pages
    if (totalPages <= 7) {

        return Array.from(
            { length: totalPages },
            (_, index) => index + 1
        );

    }


    const pages = [];

    pages.push(1);


    if (currentPage > 4) {
        pages.push("...");
    }


    const start = Math.max(2, currentPage - 1);
    const end = Math.min(
        totalPages - 1,
        currentPage + 1
    );


    for (let page = start; page <= end; page++) {
        pages.push(page);
    }


    if (currentPage < totalPages - 3) {
        pages.push("...");
    }


    pages.push(totalPages);

    return pages;
}


function updateURL() {

    const params = new URLSearchParams();

    params.set("page", currentPage);
    params.set("per_page", currentPerPage);

    const newURL =
        `${window.location.pathname}?${params.toString()}`;

    window.history.pushState({}, "", newURL);
}


function getInitialPage() {

    const params = new URLSearchParams(
        window.location.search
    );

    const page = parseInt(
        params.get("page"),
        10
    );

    const perPage = parseInt(
        params.get("per_page"),
        10
    );


    if ([20, 50, 100].includes(perPage)) {
        currentPerPage = perPage;
    }


    if (page && page > 0) {
        currentPage = page;
    }


    return currentPage;
}

// Initial load

const initialPage = getInitialPage();

loadInventory(initialPage, currentPerPage);


