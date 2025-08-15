function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function sendServiceReview(serviceId) {
    const comment = document.getElementById('message').value.trim();
    const commentInput = document.getElementById('message');
    const title = document.getElementById('subject').value.trim();
    const titleInput = document.getElementById('subject');
    const recommendationInput = document.querySelector('input[name="recommendation"]:checked');
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    const reviewTextError = document.getElementById('review-text-error');
    const reviewTitleError = document.getElementById('review-title-error');
    const errorBox = document.getElementById('review-error-box');

    if (!comment) {
        reviewTextError.textContent = 'متن دیدگاه نمی‌تواند خالی باشد.';
        reviewTextError.classList.remove('hidden');
        commentInput.classList.add('placeholder:text-warning', 'border-warning');
        return;
    }
    if (!title) {
        reviewTitleError.textContent = 'عنوان دیدگاه نمی‌تواند خالی باشد.';
        reviewTitleError.classList.remove('hidden');
        titleInput.classList.add('placeholder:text-warning', 'border-warning');
        return;
    }

    reviewTextError.textContent = '';
    reviewTextError.classList.add('hidden');
    commentInput.classList.remove('placeholder:text-warning', 'border-warning');

    reviewTitleError.textContent = '';
    reviewTitleError.classList.add('hidden');
    titleInput.classList.remove('placeholder:text-warning', 'border-warning');

    const formData = new FormData();
    formData.append('text', comment);
    formData.append('title', title);
    formData.append('service_id', serviceId);
    formData.append('csrfmiddlewaretoken', csrfToken);
    if (recommendationInput) {
        formData.append('recommendation', recommendationInput.value);
    }

    fetch('/services/add-review', {
        method: 'POST', body: formData,
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('message').value = '';
                document.getElementById('subject').value = '';
                if (recommendationInput) recommendationInput.checked = false;
                Swal.fire({
                    icon: 'success',
                    title: 'دیدگاه شما ثبت شد',
                    text: 'پس از بررسی توسط تیم، در وب‌سایت نمایش داده خواهد شد.',
                    timer: 3000,
                    showConfirmButton: false,
                    allowOutsideClick: true,
                    timerProgressBar: true
                });
            } else if (data.error) {
                errorBox.textContent = data.error;
            }
        })
        .catch(() => {
            errorBox.textContent = 'ارسال دیدگاه با خطا مواجه شد.';
        });
}

function toggleReaction(reviewId, csrfToken, reactionType) {
    fetch("/services/toggle-reaction", {
        method: 'POST', headers: {
            'X-CSRFToken': csrfToken, 'Content-Type': 'application/x-www-form-urlencoded'
        }, body: new URLSearchParams({
            review_id: reviewId, reaction: reactionType
        })
    })
        .then(res => {
            if (res.status === 403) {
                return res.json().then(data => {
                    Swal.fire({
                        icon: 'warning',
                        title: 'برای انجام این عملیات باید وارد حساب شوید.',
                        showCancelButton: true,
                        confirmButtonText: 'ورود',
                        cancelButtonText: 'انصراف',
                        allowOutsideClick: true,
                        allowEscapeKey: true,
                    }).then(result => {
                        if (result.isConfirmed) {
                            window.location.href = '/auth/';
                        }
                    });
                    throw new Error('Not authenticated');
                });
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;
            document.querySelectorAll(`[data-review-id="${reviewId}"]`).forEach(btn => {
                const type = btn.getAttribute('data-type');
                const svg = btn.querySelector('svg');
                const countSpan = btn.querySelector(`.${type}-count`);

                if (type === 'like') countSpan.textContent = data.like_count;
                if (type === 'dislike') countSpan.textContent = data.dislike_count;

                if (data.status === 'created' || data.status === 'updated') {
                    svg.setAttribute('fill', type === reactionType ? 'currentColor' : 'none');
                } else {
                    svg.setAttribute('fill', 'none');
                }
            });
        })
        .catch(e => {
            if (e.message !== 'Not authenticated') {
                Swal.fire({
                    icon: 'error', title: 'خطایی رخ داده است.', text: 'لطفا دوباره تلاش کنید.',
                });
            }
        });
}

function toggleFavorite(serviceId) {
    const csrfToken = getCookie('csrftoken');
    fetch("/services/toggle-favorite", {
        method: "POST", headers: {
            "X-CSRFToken": csrfToken, "Content-Type": "application/x-www-form-urlencoded"
        }, body: new URLSearchParams({service_id: serviceId})
    })
        .then(res => {
            if (res.status === 403) {
                Swal.fire({
                    icon: 'warning',
                    title: 'برای انجام این عملیات باید وارد حساب شوید.',
                    showCancelButton: true,
                    confirmButtonText: 'ورود',
                    cancelButtonText: 'انصراف',
                    allowOutsideClick: true,
                    allowEscapeKey: true,
                }).then(result => {
                    if (result.isConfirmed) window.location.href = '/auth/';
                });
                throw new Error('Not authenticated');
            }
            return res.json();
        })
        .then(data => {
            if (!data) return;

            const buttons = document.querySelectorAll(`[data-favorite-id="${serviceId}"]`);
            buttons.forEach(btn => {
                const icon = btn.querySelector('svg');

                if (data.status === 'added') {
                    icon.setAttribute('fill', 'currentColor');
                    btn.classList.add('active');
                } else if (data.status === 'removed') {
                    icon.setAttribute('fill', 'none');
                    btn.classList.remove('active');
                }
            });

            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: data.status === 'added' ? 'success' : 'info',
                title: data.status === 'added' ? 'به علاقه‌مندی‌ها اضافه شد' : 'از علاقه‌مندی‌ها حذف شد',
                showConfirmButton: false,
                timer: 1500
            });
        })
        .catch(e => {
            if (e.message !== 'Not authenticated') {
                Swal.fire({
                    icon: 'error', title: 'خطایی رخ داده است.', text: 'لطفا دوباره تلاش کنید.',
                });
            }
        });
}

document.addEventListener('DOMContentLoaded', function () {

    function toggleRemoveAllButton() {
        const hasFavorites = document.querySelectorAll('.remove-favorite-btn').length > 0;
        document.querySelectorAll('.remove-all-favorites-btn').forEach(btn => {
            btn.disabled = !hasFavorites;
        });
    }

    function updateFavoriteCount() {
        fetch('/favorites/count/')
            .then(res => res.json())
            .then(data => {
                document.querySelectorAll('.favorite-count').forEach(el => {
                    el.textContent = data.count;
                });
            });
    }

    function reloadFavoriteList() {
        fetch('/favorites/partial/')
            .then(res => res.text())
            .then(html => {
                document.getElementById('favorite-list').innerHTML = html;
                bindRemoveButtons();
                toggleRemoveAllButton();
                updateFavoriteCount();
            });
    }

    const container = document.getElementById('favorite-list-dashboard');

    function checkFavoriteListEmpty() {
        if (container.children.length === 0 || container.innerText.trim() === 'موردی یافت نشد.') {
            container.className = 'flex items-center justify-center';
        } else {
            container.className = 'grid gap-2 xs:grid-cols-2 md:grid-cols-3';
        }
    }

    function reloadFavoriteListDashboard() {
        fetch('/profile/favorites/partial/')
            .then(res => res.text())
            .then(html => {
                container.innerHTML = html;
                bindRemoveButtons();
                toggleRemoveAllButton();
                checkFavoriteListEmpty();
                updateFavoriteCount();
            });
    }

    function bindRemoveButtons() {
        document.querySelectorAll('.remove-favorite-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const serviceId = this.dataset.serviceId;

                Swal.fire({
                    title: 'مطمئنی؟',
                    text: 'این سرویس از علاقه‌مندی‌ها حذف بشه؟',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله',
                    cancelButtonText: 'نه',
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                }).then((result) => {
                    if (!result.isConfirmed) return;

                    const formData = new FormData();
                    formData.append('service_id', serviceId);

                    fetch('/favorites/delete/', {
                        method: 'POST', headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        }, body: formData,
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                reloadFavoriteList();
                                reloadFavoriteListDashboard();
                                Swal.fire({
                                    toast: true,
                                    position: 'top-end',
                                    icon: 'info',
                                    title: 'از علاقه‌مندی‌ها حذف شد',
                                    showConfirmButton: false,
                                    timer: 1500,
                                });
                            } else {
                                console.error('خطا در حذف:', data.message);
                            }
                        });
                });
            });
        });
    }

    document.querySelectorAll('.remove-all-favorites-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            Swal.fire({
                title: 'مطمئنی؟',
                text: 'همه موارد حذف بشن؟',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'بله',
                cancelButtonText: 'نه',
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
            }).then((result) => {
                if (!result.isConfirmed) return;

                fetch('/favorites/delete/all/', {
                    method: 'POST', headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            reloadFavoriteList();
                            reloadFavoriteListDashboard();
                            Swal.fire({
                                toast: true,
                                position: 'top-end',
                                icon: 'info',
                                title: 'همه علاقه‌مندی‌ها حذف شدن',
                                showConfirmButton: false,
                                timer: 1500,
                            });
                        }
                    });
            });
        });
    });

    bindRemoveButtons();
    toggleRemoveAllButton();
    checkFavoriteListEmpty();
    updateFavoriteCount();
});

document.addEventListener('DOMContentLoaded', function () {

    function toggleRemoveAllButton() {
        const hasVisits = document.querySelectorAll('.remove-visit-btn').length > 0;
        document.querySelectorAll('.remove-all-visits-btn').forEach(btn => {
            btn.disabled = !hasVisits;
        });
    }

    const container = document.getElementById('visit-list-dashboard');

    function checkVisitListEmpty() {
        if (container.children.length === 0 || container.innerText.trim() === 'موردی یافت نشد.') {
            container.className = 'flex items-center justify-center';
        } else {
            container.className = 'grid gap-2 xs:grid-cols-2 md:grid-cols-3';
        }
    }

    function reloadVisitListDashboard() {
        fetch('/profile/visits/partial/')
            .then(res => res.text())
            .then(html => {
                container.innerHTML = html;
                bindRemoveButtons();
                toggleRemoveAllButton();
                checkVisitListEmpty();
            });
    }

    function bindRemoveButtons() {
        document.querySelectorAll('.remove-visit-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const serviceId = this.dataset.serviceId;

                Swal.fire({
                    title: 'مطمئنی؟',
                    text: 'این سرویس از علاقه‌مندی‌ها حذف بشه؟',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله',
                    cancelButtonText: 'نه',
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                }).then((result) => {
                    if (!result.isConfirmed) return;

                    const formData = new FormData();
                    formData.append('service_id', serviceId);

                    fetch('/visits/delete/', {
                        method: 'POST', headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        }, body: formData,
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                reloadVisitListDashboard();
                                Swal.fire({
                                    toast: true,
                                    position: 'top-end',
                                    icon: 'info',
                                    title: 'از علاقه‌مندی‌ها حذف شد',
                                    showConfirmButton: false,
                                    timer: 1500,
                                });
                            } else {
                                console.error('خطا در حذف:', data.message);
                            }
                        });
                });
            });
        });
    }

    document.querySelectorAll('.remove-all-visits-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            Swal.fire({
                title: 'مطمئنی؟',
                text: 'همه موارد حذف بشن؟',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'بله',
                cancelButtonText: 'نه',
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
            }).then((result) => {
                if (!result.isConfirmed) return;

                fetch('/visits/delete/all/', {
                    method: 'POST', headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    },
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            reloadVisitListDashboard();
                            Swal.fire({
                                toast: true,
                                position: 'top-end',
                                icon: 'info',
                                title: 'همه علاقه‌مندی‌ها حذف شدن',
                                showConfirmButton: false,
                                timer: 1500,
                            });
                        }
                    });
            });
        });
    });

    bindRemoveButtons();
    toggleRemoveAllButton();
    checkVisitListEmpty();
});

document.addEventListener('DOMContentLoaded', function () {

    function toggleReadAllButton() {
        const unreadNotifs = document.querySelectorAll('.unread-notification');
        const hasUnread = unreadNotifs.length > 0;

        document.querySelectorAll('.read-all-notifications-btn').forEach(btn => {
            btn.disabled = !hasUnread;
            btn.classList.toggle('opacity-45', !hasUnread);
            btn.classList.toggle('cursor-not-allowed', !hasUnread);
        });
    }

    function reloadNotifListDashboard() {
        document.querySelectorAll('.notifications-dashboard').forEach(container => {
            const url = container.dataset.fetchUrl;

            fetch(url)
                .then(res => res.text())
                .then(html => {
                    container.innerHTML = html;
                    bindReadButtons();
                    toggleReadAllButton();
                    checkReadListEmpty(container);
                });
        });
    }

    function checkReadListEmpty(container) {
        if (container.children.length === 0 || container.innerText.trim() === 'موردی یافت نشد.') {
            container.className = 'flex items-center justify-center';
        }
    }

    function markNotifAsReadEverywhere(notifId) {
        document.querySelectorAll(`[data-id="${notifId}"]`).forEach(card => {
            card.classList.add('opacity-45');
            const btn = card.querySelector('.read-notification-btn');
            if (btn) btn.disabled = true;
        });
    }

    function bindReadButtons() {
        document.querySelectorAll('.read-notification-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const notifId = this.dataset.notifId;

                const formData = new FormData();
                formData.append('notif_id', notifId);

                fetch('/notifications/read/', {
                    method: 'POST', headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                    }, body: formData,
                })
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === 'ok') {
                            const notifCard = btn.closest('.notification-card');
                            if (notifCard) notifCard.classList.add('opacity-45');
                            btn.disabled = true;

                            markNotifAsReadEverywhere(notifId);
                            updateUnreadCount();
                            toggleReadAllButton();
                            checkReadListEmpty();
                        } else {
                            console.error('خطا در خواندن:', data.message);
                        }
                    });
            });
        });
    }

    document.querySelectorAll('.read-all-notifications-btn').forEach(btn => {
        btn.addEventListener('click', function () {

            fetch('/notifications/read/all/', {
                method: 'POST', headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
                .then(res => res.json())
                .then(data => {
                    {
                        reloadNotifListDashboard();
                        updateUnreadCount();
                        Swal.fire({
                            toast: true,
                            position: 'top',
                            icon: 'info',
                            title: 'تمام اعلان ها خوانده شدند',
                            showConfirmButton: false,
                            timer: 1500,
                        });
                    }
                });
        });
    });

    bindReadButtons();
    toggleReadAllButton();
    checkReadListEmpty();
});

function loadCartPartial() {
    const cartElement = document.getElementById('cart-partial');
    const url = cartElement.getAttribute('data-fetch-url');

    fetch(url)
        .then(res => res.text())
        .then(html => {
            cartElement.innerHTML = html;
            showOrderItemsCount();
        });
}

function addServiceToCart(serviceId) {
    const count = parseInt(document.querySelector('.service-count').value);
    const optionId = document.getElementById('option-select').value;
    const scheduleId = document.getElementById('schedule-select').value;

    if (!optionId || !scheduleId) {
        Swal.fire({
            title: "خطا",
            text: "لطفاً نوع تبلیغ و زمان را انتخاب کنید",
            icon: "error",
            confirmButtonColor: "#3085d6",
            confirmButtonText: "باشه",
            showCloseButton: true,
        });
        return;
    }

    $.get(`/services/add-to-cart?service_id=${serviceId}&option_id=${optionId}&schedule_id=${scheduleId}&count=${count}`)
        .then(res => {
            Swal.fire({
                title: "اعلان",
                text: res.message,
                icon: res.status === 'success' ? "success" : "error",
                confirmButtonText: res.confirm_button_text,
                showCloseButton: true,
            }).then(result => {
                if (res.status === 'success' && result.isConfirmed) {
                    window.location.href = "/orders/cart";
                }
            });
        });
}

function bindCartItemEvents() {
    document.querySelectorAll('.cart-item-card').forEach(card => {
        const increaseBtn = card.querySelector(".increase-qty");
        const decreaseBtn = card.querySelector(".decrease-qty");
        const countInput = card.querySelector(".service-count");

        if (!increaseBtn || !decreaseBtn || !countInput) return;

        increaseBtn.addEventListener("click", function () {
            countInput.value = parseInt(countInput.value) + 1;
        });

        decreaseBtn.addEventListener("click", function () {
            const current = parseInt(countInput.value);
            if (current > 1) countInput.value = current - 1;
        });
    });
}

document.addEventListener("DOMContentLoaded", bindCartItemEvents);

document.addEventListener('DOMContentLoaded', function () {

    function reloadServiceList() {
        fetch('/services/partial/')
            .then(res => res.text())
            .then(html => {
                document.getElementById('service-list').innerHTML = html;
                bindRemoveButtons();
            });
    }

    const container = document.getElementById('service-list-dashboard');

    function checkFavoriteListEmpty() {
        if (container.children.length === 0 || container.innerText.trim() === 'موردی یافت نشد.') {
            container.className = 'flex items-center justify-center';
        } else {
            container.className = 'grid gap-2 xs:grid-cols-2 md:grid-cols-3';
        }
    }

    function reloadServiceListDashboard() {
        fetch('/profile/services/partial/')
            .then(res => res.text())
            .then(html => {
                container.innerHTML = html;
                bindRemoveButtons();
                checkFavoriteListEmpty();
            });
    }

    function bindRemoveButtons() {
        document.querySelectorAll('.remove-service-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const serviceId = this.dataset.serviceId;

                Swal.fire({
                    title: 'مطمئنی؟',
                    text: 'این سرویس از خدمت های شما حذف بشه؟',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله',
                    cancelButtonText: 'نه',
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                }).then((result) => {
                    if (!result.isConfirmed) return;

                    const formData = new FormData();
                    formData.append('service_id', serviceId);

                    fetch('/profile/services/delete/', {
                        method: 'POST', headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        }, body: formData,
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.status === 'ok') {
                                reloadServiceList();
                                reloadServiceListDashboard();
                                Swal.fire({
                                    toast: true,
                                    position: 'top-end',
                                    icon: 'info',
                                    title: 'خدمت حذف شد',
                                    showConfirmButton: false,
                                    timer: 1500,
                                });
                            } else {
                                console.error('خطا در حذف:', data.message);
                            }
                        });
                });
            });
        });
    }

    bindRemoveButtons();
    checkFavoriteListEmpty();
});

document.addEventListener("DOMContentLoaded", () => {

    function setupServiceForm({
                                  formId,
                                  optionFetchUrl,
                                  scheduleFetchUrl,
                                  optionPrefix = "option",
                                  schedulePrefix = "schedule",
                                  provinceSelectId = "province",
                                  cityDropdownId = "city-dropdown",
                                  cityOptionsId = "city-options",
                                  selectedCitiesDivId = "selected-cities",
                                  selectedCitiesInputId = "selected-cities-input",
                                  preselectedCitiesInputId = "preselected-cities"
                              }) {

        const formatNumberWithCommas = (value) => value.replace(/\B(?=(\d{3})+(?!\d))/g, "٬");

        function bindPriceFormatter(input) {
            input.type = "text";
            input.style.direction = "ltr";
            const initialValue = input.defaultValue || input.value;
            if (initialValue.trim() !== "") {
                let raw = initialValue.replace(/[٬,]/g, '').replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
                input.value = formatNumberWithCommas(raw);
            }
            input.addEventListener("input", () => {
                let raw = input.value.replace(/[٬,]/g, '').replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
                input.value = formatNumberWithCommas(raw);
            });
        }

        document.querySelectorAll("input[name$='unit_price']").forEach(bindPriceFormatter);

        document.addEventListener("submit", e => {
            if (e.target.id === formId) {
                e.target.querySelectorAll("input[name$='unit_price']").forEach(input => {
                    let raw = input.value.replace(/[٬,]/g, '').replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
                    input.value = raw;
                });
            }
        }, true);


        function showEmptyMessage(formset, prefix) {
            if (!formset.querySelector(".empty-message")) {
                const msg = document.createElement("div");
                msg.className = "empty-message col-span-full flex flex-col items-center justify-center gap-4 rounded-lg backdrop-blur-sm";
                msg.innerHTML = `
                <h5 class="text-center pb-4">هیچ آیتمی اضافه نشده</h5>
                <button type="button" class="btn-primary flex items-center gap-1 px-4 py-2 add-${prefix}">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
                        <path d="M5 12h14"></path>
                        <path d="M12 5v14"></path>
                    </svg>
                    ${prefix === "option" ? "آپشن جدید" : "زمان‌بندی جدید"}
                </button>`;
                formset.appendChild(msg);
            }
        }

        function hideEmptyMessage(formset) {
            const msg = formset.querySelector(".empty-message");
            if (msg) msg.remove();
        }

        function updateEmptyState(wrapper, formClass, prefix) {
            const targetFormset = prefix === "option"
                ? wrapper.querySelector(".option-formset")
                : wrapper.querySelector(".schedule-formset");

            const visibleForms = targetFormset.querySelectorAll(`.${formClass}:not([style*="display: none"])`);
            const mainButton = wrapper.querySelector(`.add-${prefix}`);

            if (visibleForms.length === 0) {
                if (mainButton) mainButton.style.display = "none";
                showEmptyMessage(wrapper, prefix);
            } else {
                if (mainButton) mainButton.style.display = "flex";
                hideEmptyMessage(wrapper, prefix);
            }
        }

        function reindexForms(formset, prefix, formClass) {
            const forms = formset.querySelectorAll(`.${formClass}`);
            const totalFormsInput = document.querySelector(`#id_${prefix}-TOTAL_FORMS`);
            forms.forEach((form, index) => {
                const regex = new RegExp(`${prefix}-(\\d+|__prefix__)`, "g");
                form.querySelectorAll("input, select, textarea, label").forEach(el => {
                    if (el.name) el.name = el.name.replace(regex, `${prefix}-${index}`);
                    if (el.id) el.id = el.id.replace(regex, `${prefix}-${index}`);
                    if (el.htmlFor) el.htmlFor = el.htmlFor.replace(regex, `${prefix}-${index}`);
                });
            });
            totalFormsInput.value = forms.length;
        }

        function setupDynamicForms({addButtonSelector, formsetSelector, fetchUrl, formClass, removeBtnClass, prefix}) {
            document.querySelectorAll(addButtonSelector).forEach(addBtn => {
                const wrapper = addBtn.closest(".dynamic-form-wrapper");
                const formset = wrapper.querySelector(formsetSelector);
                const totalFormsInput = document.querySelector(`#id_${prefix}-TOTAL_FORMS`);

                updateEmptyState(wrapper, formClass, prefix);

                wrapper.addEventListener("click", e => {
                    if (e.target.closest(`.add-${prefix}`) && e.target.closest(".empty-message")) {
                        addBtn.click();
                    }
                });

                addBtn.addEventListener("click", () => {
                    const formIndex = parseInt(totalFormsInput.value);
                    fetch(`${fetchUrl}?prefix=${prefix}&index=${formIndex}`, {
                        method: 'GET',
                        headers: {'X-Requested-With': 'XMLHttpRequest'}
                    })
                        .then(res => res.json())
                        .then(data => {
                            if (data.success) {
                                let tempDiv = document.createElement('div');
                                tempDiv.innerHTML = data.html;
                                let newForm = tempDiv.firstElementChild;

                                const idInput = newForm.querySelector(`input[name$='-id']`);
                                if (idInput) idInput.remove();

                                formset.appendChild(newForm);

                                reindexForms(formset, prefix, formClass);
                                updateEmptyState(wrapper, formClass, prefix);
                                newForm.querySelectorAll("input[name$='unit_price']").forEach(bindPriceFormatter);
                            }
                        });
                });

                formset.addEventListener("click", e => {
                    if (e.target.classList.contains(removeBtnClass)) {
                        const item = e.target.closest(`.${formClass}`);
                        Swal.fire({
                            title: 'آیا مطمئنی؟',
                            text: "این عملیات قابل بازگشت نیست!",
                            icon: 'warning',
                            showCancelButton: true,
                            confirmButtonText: 'بله، حذف کن',
                            cancelButtonText: 'نه، منصرف شدم',
                            reverseButtons: true
                        }).then(result => {
                            if (result.isConfirmed) {
                                const id = item.getAttribute("data-id");
                                const deleteInput = item.querySelector(`input[name$='-DELETE']`);
                                if (!id || id === "None" || id === "") {
                                    item.remove();
                                    reindexForms(formset, prefix, formClass);
                                    updateEmptyState(wrapper, formClass, prefix);

                                    Swal.fire({
                                        toast: true,
                                        position: 'top-end',
                                        icon: 'success',
                                        title: 'با موفقیت حذف شد',
                                        showConfirmButton: false,
                                        timer: 2000
                                    });
                                    return;
                                }

                                fetch(`/profile/services/${prefix}/delete/${id}`, {
                                    method: 'POST',
                                    headers: {
                                        'X-Requested-With': 'XMLHttpRequest',
                                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                    }
                                })
                                    .then(res => res.json())
                                    .then(data => {
                                        if (data.success) {
                                            if (deleteInput) {
                                                deleteInput.checked = true;
                                                item.style.display = 'none';
                                            } else {
                                                item.remove();
                                            }
                                            reindexForms(formset, prefix, formClass);
                                            updateEmptyState(wrapper, formClass, prefix);

                                            Swal.fire({
                                                toast: true,
                                                position: 'top-end',
                                                icon: 'success',
                                                title: data.message || 'با موفقیت حذف شد',
                                                showConfirmButton: false,
                                                timer: 2000
                                            });
                                        } else {
                                            Swal.fire({
                                                icon: 'error',
                                                title: 'خطا در حذف',
                                                text: data.error || 'امکان حذف این مورد وجود ندارد.',
                                            });
                                            // حذف فیزیکی انجام نشود چون خطا وجود دارد
                                        }
                                    })
                                    .catch(() => {
                                        Swal.fire({
                                            icon: 'error',
                                            title: 'خطا در اتصال',
                                            text: 'ارتباط با سرور برقرار نشد.'
                                        });
                                    });
                            }
                        });
                    }
                });
            });
        }

        const provinceSelect = document.getElementById(provinceSelectId);
        const dropdownBtn = document.getElementById(cityDropdownId);
        const cityOptions = document.getElementById(cityOptionsId);
        const selectedCitiesDiv = document.getElementById(selectedCitiesDivId);
        const selectedCitiesInput = document.getElementById(selectedCitiesInputId);
        const preselectedCitiesInput = document.getElementById(preselectedCitiesInputId);

        let selectedCities = [];

        if (preselectedCitiesInput && preselectedCitiesInput.value.trim() !== "") {
            try {
                selectedCities = JSON.parse(preselectedCitiesInput.value);
            } catch {
                selectedCities = [];
            }
        }

        function renderSelectedCities() {
            selectedCitiesDiv.innerHTML = "";
            selectedCities.forEach(city => {
                const tag = document.createElement("div");
                tag.className = "bg-indigo-500 text-white text-sm px-2 py-1 rounded flex items-center gap-1";
                tag.innerHTML = `${city.name} <button type="button" data-id="${city.id}" class="remove-city i-lucide-x size-5"></button>`;
                selectedCitiesDiv.appendChild(tag);
            });
            selectedCitiesInput.value = selectedCities.map(c => c.id).join(",");
        }

        function fetchCities(provinceId) {
            fetch(`/profile/services/load-cities/?province=${provinceId}`)
                .then(res => res.json())
                .then(data => {
                    cityOptions.innerHTML = "";
                    data.cities.forEach(city => {
                        const checked = selectedCities.some(c => c.id === city.id) ? "checked" : "";
                        const item = document.createElement("div");
                        item.className = "px-4 py-2 hover:bg-muted cursor-pointer flex items-center gap-2";
                        item.innerHTML = `
                            <input type="checkbox" class="city-checkbox" data-id="${city.id}" data-name="${city.name_fa}" ${checked}>
                            <span>${city.name_fa}</span>
                        `;
                        cityOptions.appendChild(item);
                    });
                });
        }

        provinceSelect.addEventListener("change", e => fetchCities(e.target.value));

        dropdownBtn.addEventListener("click", () => cityOptions.classList.toggle("hidden"));

        cityOptions.addEventListener("change", e => {
            if (e.target.classList.contains("city-checkbox")) {
                const cityId = parseInt(e.target.dataset.id);
                const cityName = e.target.dataset.name;
                if (e.target.checked) {
                    if (!selectedCities.some(c => c.id === cityId)) selectedCities.push({id: cityId, name: cityName});
                } else {
                    selectedCities = selectedCities.filter(c => c.id !== cityId);
                }
                renderSelectedCities();
            }
        });

        selectedCitiesDiv.addEventListener("click", e => {
            if (e.target.classList.contains("remove-city")) {
                const cityId = parseInt(e.target.dataset.id);
                selectedCities = selectedCities.filter(c => c.id !== cityId);
                renderSelectedCities();
                const checkbox = cityOptions.querySelector(`.city-checkbox[data-id="${cityId}"]`);
                if (checkbox) checkbox.checked = false;
            }
        });

        renderSelectedCities();
        fetchCities(provinceSelect.value);

        const form = document.getElementById(formId);
        form.addEventListener("submit", e => {
            e.preventDefault();
            const formData = new FormData(form);
            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {"X-Requested-With": "XMLHttpRequest"}
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'با موفقیت ذخیره شد',
                            text: 'در حال بازگشت به لیست سرویس‌ها...',
                            timer: 2000,
                            timerProgressBar: true,
                            showConfirmButton: false
                        }).then(() => window.location.href = data.redirect_url);
                    } else {
                        const errorContainer = document.getElementById("form-errors");
                        errorContainer.innerHTML = data.errors_html;
                        errorContainer.scrollIntoView({behavior: 'smooth', block: 'center'});
                    }
                })
                .catch(() => Swal.fire({
                    icon: 'error',
                    title: 'مشکل در ارسال فرم',
                    text: 'لطفاً دوباره تلاش کنید.',
                    timer: 3000
                }));
        });

        setupDynamicForms({
            addButtonSelector: `.add-${optionPrefix}`,
            formsetSelector: ".option-formset",
            fetchUrl: optionFetchUrl,
            formClass: "option-form",
            removeBtnClass: "remove-option",
            prefix: optionPrefix
        });

        setupDynamicForms({
            addButtonSelector: `.add-${schedulePrefix}`,
            formsetSelector: ".schedule-formset",
            fetchUrl: scheduleFetchUrl,
            formClass: "schedule-form",
            removeBtnClass: "remove-schedule",
            prefix: schedulePrefix
        });
    }

    // بخش آپلود تصویر - بدون تغییر
    document.querySelectorAll('.image-upload-wrapper').forEach(wrapper => {
        const dropzone = wrapper.querySelector('#dropzone');
        const input = wrapper.querySelector('#imageInput');
        const loader = wrapper.querySelector('#loader');
        const cropModal = document.getElementById('cropModal');
        const cropImage = document.getElementById('cropImage');
        const cancelCrop = document.getElementById('cancelCrop');
        const confirmCrop = document.getElementById('confirmCrop');
        let cropper;

        cancelCrop.className = "btn-warning w-full rounded-lg px-4 py-2 md:w-auto";
        confirmCrop.className = "btn-primary w-full rounded-lg px-4 py-2 md:w-auto";

        const handleFileSelect = () => {
            if (!input.files.length) return;
            const file = input.files[0];
            const reader = new FileReader();
            reader.onload = e => {
                cropImage.src = e.target.result;
                document.querySelector('[data-modal-hide="profile_image-modal"]')?.click();
                cropModal.classList.remove('hidden');
                if (cropper) cropper.destroy();
                cropper = new Cropper(cropImage, {aspectRatio: 1, viewMode: 1});
            };
            reader.readAsDataURL(file);
        };

        dropzone.addEventListener('drop', e => {
            e.preventDefault();
            input.files = e.dataTransfer.files;
            dropzone.classList.remove('border-blue-600', 'bg-blue-50');
            handleFileSelect();
        });
        dropzone.addEventListener('click', () => input.click());
        dropzone.addEventListener('dragover', e => {
            e.preventDefault();
            dropzone.classList.add('border-blue-600', 'bg-blue-50');
        });
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('border-blue-600', 'bg-blue-50');
        });
        input.addEventListener('change', handleFileSelect);

        cancelCrop.addEventListener('click', () => {
            cropModal.classList.add('hidden');
            if (cropper) cropper.destroy();
        });

        confirmCrop.addEventListener('click', () => {
            loader.classList.remove('hidden');
            cropper.getCroppedCanvas().toBlob(blob => {
                const formData = new FormData();
                formData.append(input.name, blob, 'cropped_image.png');
                formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

                fetch(wrapper.dataset.uploadUrl, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                })
                    .then(res => res.json())
                    .then(data => {
                        loader.classList.add('hidden');
                        cropModal.classList.add('hidden');
                        if (cropper) cropper.destroy();
                        if (data.success) {
                            Swal.fire({
                                toast: true,
                                position: 'top-end',
                                icon: 'success',
                                title: 'تصویر با موفقیت آپلود شد',
                                showConfirmButton: false,
                                timer: 2000,
                                timerProgressBar: true,
                            });
                        } else {
                            Swal.fire({icon: 'error', title: 'خطا در آپلود', text: 'مشکلی پیش آمد. لطفاً دوباره تلاش کنید.'});
                        }
                    })
                    .catch(() => {
                        loader.classList.add('hidden');
                        cropModal.classList.add('hidden');
                        if (cropper) cropper.destroy();
                        Swal.fire({icon: 'error', title: 'خطا در اتصال', text: 'ارتباط با سرور برقرار نشد.'});
                    });
            });
        });
    });

    if (document.getElementById("edit-service-form")) {
        setupServiceForm({
            formId: "edit-service-form",
            optionFetchUrl: "/profile/services/option/add/",
            scheduleFetchUrl: "/profile/services/schedule/add/",
            optionPrefix: "option",
            schedulePrefix: "schedule",
            provinceSelectId: "province",
            cityDropdownId: "city-dropdown",
            cityOptionsId: "city-options",
            selectedCitiesDivId: "selected-cities",
            selectedCitiesInputId: "selected-cities-input",
            preselectedCitiesInputId: "preselected-cities"
        });
    } else if (document.getElementById("create-service-form")) {
        setupServiceForm({
            formId: "create-service-form",
            optionFetchUrl: "/profile/services/option/add/",
            scheduleFetchUrl: "/profile/services/schedule/add/",
            optionPrefix: "option",
            schedulePrefix: "schedule",
            provinceSelectId: "province",
            cityDropdownId: "city-dropdown",
            cityOptionsId: "city-options",
            selectedCitiesDivId: "selected-cities",
            selectedCitiesInputId: "selected-cities-input",
            preselectedCitiesInputId: "preselected-cities"
        });
    }

});


document.addEventListener('DOMContentLoaded', function () {
    loadCartPartial();
});