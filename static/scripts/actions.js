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

function setupDynamicForms({
                               addButtonSelector,
                               formsetSelector,
                               fetchUrl,
                               deleteUrlBase,
                               formClass,
                               removeBtnClass,
                               prefix
                           }) {
    document.querySelectorAll(addButtonSelector).forEach(addBtn => {
        const wrapper = addBtn.closest(".dynamic-form-wrapper");
        const formset = wrapper.querySelector(formsetSelector);
        const totalFormsInput = document.querySelector(`#id_${prefix}-TOTAL_FORMS`);

        const persianToEnglishNumber = (str) => {
            return str.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
        };

        function formatNumberWithCommas(value) {
            return value.replace(/\B(?=(\d{3})+(?!\d))/g, "٬");
        }

        function setupPriceFormatting(root) {
            const priceInputs = root.querySelectorAll("input[name$='unit_price']");
            priceInputs.forEach(input => {
                input.type = "text";
                input.style.direction = "rtl";

                if (input.value.trim() !== "") {
                    let raw = input.value
                        .replace(/[٬,]/g, '')
                        .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
                    input.value = formatNumberWithCommas(raw);
                }

                input.addEventListener("input", function (e) {
                    const el = e.target;
                    let cursorPosition = el.selectionStart;

                    let english = persianToEnglishNumber(el.value).replace(/\D/g, "");

                    const oldLength = el.value.length;

                    let formatted = formatNumberWithCommas(english);

                    el.value = formatted;

                    const newLength = formatted.length;
                    cursorPosition = cursorPosition + (newLength - oldLength);
                    el.setSelectionRange(cursorPosition, cursorPosition);
                });
            });
        }

        setupPriceFormatting(formset);

        addBtn.addEventListener("click", function () {
            const formIndex = parseInt(totalFormsInput.value);

            fetch(`${fetchUrl}?prefix=${prefix}&index=${formIndex}`, {
                method: 'GET',
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        formset.insertAdjacentHTML('beforeend', data.html);
                        totalFormsInput.value = formIndex + 1;

                        const newForm = formset.lastElementChild;
                        setupPriceFormatting(newForm);
                    } else {
                        console.error(data.errors);
                    }
                });
        });

        formset.addEventListener("click", function (e) {
            if (e.target.classList.contains(removeBtnClass)) {
                const item = e.target.closest(`.${formClass}`);
                const deleteInput = item.querySelector(`input[name$="-DELETE"]`);
                const id = item.getAttribute("data-id");

                Swal.fire({
                    title: 'آیا مطمئنی؟',
                    text: "این عملیات قابل بازگشت نیست!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله، حذف کن',
                    cancelButtonText: 'نه، منصرف شدم',
                    reverseButtons: true
                }).then((result) => {
                    if (result.isConfirmed) {
                        const isNew = !id || id === "None" || id === "";

                        if (isNew) {
                            item.remove();
                            const visibleForms = formset.querySelectorAll(`.${formClass}:not([style*="display: none"])`);
                            totalFormsInput.value = visibleForms.length;
                        } else {
                            if (deleteInput) {
                                deleteInput.checked = true;
                                item.style.display = "none";
                            } else {
                                console.error("DELETE input not found for existing form");
                            }
                        }
                    }
                });
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const csrfToken = "{{ csrf_token }}";

    setupDynamicForms({
        addButtonSelector: ".add-option",
        formsetSelector: ".option-formset",
        fetchUrl: "/profile/services/option/add/",
        deleteUrlBase: "/profile/services/option/delete/",
        formClass: "option-form",
        removeBtnClass: "remove-option",
        csrfToken: csrfToken,
        prefix: "option"
    });

    document.querySelectorAll("input[name$='unit_price']").forEach(input => {
        input.style.direction = "ltr";

        if (input.value.trim() !== "") {
            let raw = input.value
                .replace(/[٬,]/g, '')
                .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
            input.value = raw.replace(/\B(?=(\d{3})+(?!\d))/g, "٬");
        }
    });

    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function () {
            form.querySelectorAll("input[name$='unit_price']").forEach(input => {
                let raw = input.value
                    .replace(/[٬,]/g, '')
                    .replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d));
                input.value = raw;
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    loadCartPartial();
});