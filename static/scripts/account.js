document.addEventListener("DOMContentLoaded", () => {
    const modals = document.querySelectorAll(".field-modal");

    modals.forEach(modal => {
        // const fieldName = modal.dataset.field;
        const fieldName = modal.dataset.field;
        const submitBtn = modal.querySelector(".submit-btn");
        const input = modal.querySelector(".modal-input");
        const errorText = modal.querySelector(".error-text");
        const url = modal.dataset.url;

        modal.querySelectorAll(".modal-input").forEach(input => {
            input.addEventListener("keydown", function (e) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    submitBtn.click();
                }
            });
        });

        modal.addEventListener("shown.bs.modal", () => {
            input.value = "";
            errorText.textContent = "";
        });

        submitBtn.addEventListener("click", () => {
            errorText.textContent = "";
            const icon = modal.querySelector("i");

            if (icon) icon.classList.add("hidden");

            const form = modal.querySelector("form");
            const formData = new FormData(form);

            fetch(url, {
                method: "POST",
                headers: {"X-CSRFToken": getCookie("csrftoken")},
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            toast: true,
                            position: "top-end",
                            icon: "success",
                            title: "تغییر با موفقیت انجام شد.",
                            showConfirmButton: false,
                            timer: 1500
                        }).then(() => {
                            window.location.href = data.redirect_url;
                        });
                    } else if (data.error_type && data.error_message) {
                        errorText.textContent = data.error_message;
                        if (icon) icon.classList.remove("hidden");
                    } else if (data.errors && data.errors[fieldName]) {
                        errorText.textContent = data.errors[fieldName][0].message;
                        if (icon) icon.classList.remove("hidden");
                    }
                });
        });
    });

    const closeBtns = document.querySelectorAll(".modal-close-btn");

    closeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const modal = btn.closest(".field-modal");
            const input = modal.querySelector(".modal-input");
            const errorText = modal.querySelector(".error-text");
            input.value = "";
            errorText.textContent = "";
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
