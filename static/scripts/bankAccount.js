document.addEventListener("DOMContentLoaded", () => {
    const forms = ["create-bank-account-form", "edit-bank-account-form"];

    forms.forEach(formId => {
        const form = document.getElementById(formId);
        if (!form) return;

        form.querySelectorAll("input[type='text']").forEach(input => {
            input.addEventListener("input", (e) => {
                let value = e.target.value;
                value = value.replace(/[۰-۹]/g, d => "۰۱۲۳۴۵۶۷۸۹".indexOf(d));
                value = value.replace(/[^0-9]/g, "");
                e.target.value = value;
            });
        });

        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const url = form.action;
            const formData = new FormData(form);

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value
                },
                body: formData
            });

            const data = await response.json();
            const errorBox = document.getElementById("form-errors");
            errorBox.innerHTML = "";

            if (data.success) {
                Swal.fire({
                    toast: true,
                    position: 'top-end',
                    icon: 'success',
                    title: data.message,
                    showConfirmButton: false,
                    timer: 2000,
                    timerProgressBar: true,
                }).then(() => {
                    window.location.href = data.redirect_url;
                });
            } else {
                if (data.errors) {
                    for (let field in data.errors) {
                        data.errors[field].forEach(msg => {
                            const div = document.createElement("div");
                            div.className = "bg-red-100 text-red-600 rounded p-4 mb-2 flex items-center gap-2";

                            const icon = document.createElement("i");
                            icon.className = "i-lucide-circle-alert text-red-600";

                            const text = document.createElement("span");
                            text.innerText = msg;

                            div.appendChild(icon);
                            div.appendChild(text);
                            errorBox.appendChild(div);
                        });
                    }
                } else {
                    const div = document.createElement("div");
                    div.className = "bg-red-100 text-red-600 rounded p-4";
                    div.innerText = "مشکلی پیش آمده، دوباره تلاش کنید.";
                    errorBox.appendChild(div);
                }
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('bank-list-dashboard');

    function checkBankListEmpty() {
        if (container.children.length === 0 || container.innerText.trim() === 'موردی یافت نشد.') {
            container.className = 'flex items-center justify-center';
        }
    }

    function bindRemoveButtons() {
        document.querySelectorAll('.remove-bank-account-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const accountId = btn.getAttribute("data-id");

                Swal.fire({
                    title: 'مطمئنی؟',
                    text: 'این حساب بانکی از پروفایل‌های شما حذف بشه؟',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله',
                    cancelButtonText: 'خیر',
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                }).then((result) => {
                    if (!result.isConfirmed) return;

                    const formData = new FormData();
                    formData.append("id", accountId);

                    fetch('/profile/bank-account/delete/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        },
                        body: formData,
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                const row = document.getElementById(`bank-account-${accountId}`);
                                if (row) row.remove();

                                const rows = container.querySelectorAll('tr[id^="bank-account-"]');
                                if (rows.length === 0) {
                                    reloadBankListDashboard();
                                }

                                Swal.fire({
                                    toast: true,
                                    position: 'top-end',
                                    icon: 'info',
                                    title: 'حساب بانکی حذف شد',
                                    showConfirmButton: false,
                                    timer: 2500,
                                });
                            } else {
                                console.error('خطا در حذف:', data.message);
                            }
                        });
                });
            });
        });
    }

    function reloadBankListDashboard() {
        fetch('/profile/bank-account/partial/')
            .then(res => res.text())
            .then(html => {
                container.innerHTML = html;
                bindRemoveButtons();
                checkBankListEmpty();
            });
    }

    bindRemoveButtons();
    checkBankListEmpty();
});
