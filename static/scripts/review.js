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
        method: 'POST',
        body: formData,
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
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            review_id: reviewId,
            reaction: reactionType
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
                    icon: 'error',
                    title: 'خطایی رخ داده است.',
                    text: 'لطفا دوباره تلاش کنید.',
                });
            }
        });
}
