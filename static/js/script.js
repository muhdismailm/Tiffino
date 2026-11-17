
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // 1. SIDEBAR TOGGLE
    // =====================================

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("active");
        });
    }


    // =====================================
    // 2. CONFIRMATION BEFORE ACTIONS
    // =====================================

    document.querySelectorAll("[data-confirm]").forEach(function (element) {

        element.addEventListener("click", function (event) {

            const message = element.dataset.confirm || "Are you sure?";

            if (!confirm(message)) {
                event.preventDefault();
            }

        });

    });


    // =====================================
    // 3. AUTO DISMISS ALERTS
    // =====================================

    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(function (alert) {

        setTimeout(function () {

            if (typeof bootstrap !== "undefined") {
                const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
                alertInstance.close();
            }

        }, 4000);

    });


    // =====================================
    // 4. PASSWORD VISIBILITY
    // =====================================

    document.querySelectorAll("[data-toggle-password]").forEach(function (button) {

        button.addEventListener("click", function () {

            const input = document.querySelector(button.dataset.togglePassword);

            if (!input) return;

            if (input.type === "password") {
                input.type = "text";
                button.textContent = "Hide";
            } else {
                input.type = "password";
                button.textContent = "Show";
            }

        });

    });


    // =====================================
    // 5. SELECT ALL CHECKBOXES
    // =====================================

    const selectAll = document.getElementById("selectAll");

    if (selectAll) {

        selectAll.addEventListener("change", function () {

            document.querySelectorAll(".item-checkbox").forEach(function (checkbox) {
                checkbox.checked = selectAll.checked;
            });

        });

    }


    // =====================================
    // 6. MEAL SELECTION
    // =====================================

    const mealCheckboxes = document.querySelectorAll(".meal-checkbox");

    mealCheckboxes.forEach(function (checkbox) {

        checkbox.addEventListener("change", function () {

            const mealOption = checkbox.closest(".meal-option");

            if (mealOption) {
                mealOption.classList.toggle("selected", checkbox.checked);
            }

        });

    });


    // =====================================
    // 7. DATE VALIDATION
    // =====================================

    const dateInputs = document.querySelectorAll('input[type="date"][data-no-past]');

    const today = new Date();
    const localToday = new Date(
        today.getTime() - today.getTimezoneOffset() * 60000
    ).toISOString().split("T")[0];

    dateInputs.forEach(function (input) {
        input.min = localToday;
    });


    // =====================================
    // 8. LEAVE DATE VALIDATION
    // =====================================

    const fromDate = document.getElementById("from_date");
    const toDate = document.getElementById("to_date");

    if (fromDate && toDate) {

        fromDate.addEventListener("change", function () {

            toDate.min = fromDate.value;

            if (toDate.value && toDate.value < fromDate.value) {
                toDate.value = fromDate.value;
            }

        });

    }


    // =====================================
    // 9. CURRENT DATE DISPLAY
    // =====================================

    const currentDate = document.getElementById("currentDate");

    if (currentDate) {

        currentDate.textContent = new Date().toLocaleDateString("en-IN", {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        });

    }


    // =====================================
    // 10. TABLE SEARCH
    // =====================================

    const tableSearch = document.getElementById("tableSearch");

    if (tableSearch) {

        tableSearch.addEventListener("input", function () {

            const searchValue = tableSearch.value.toLowerCase();
            const tableRows = document.querySelectorAll("#dataTable tbody tr");

            tableRows.forEach(function (row) {

                row.style.display = row.textContent.toLowerCase().includes(searchValue)
                    ? ""
                    : "none";

            });

        });

    }

});
