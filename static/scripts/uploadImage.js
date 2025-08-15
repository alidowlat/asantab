document.addEventListener('DOMContentLoaded', () => {
    const dropzone = document.getElementById('dropzone');
    const input = document.getElementById('imageInput');
    const loader = document.getElementById('loader');
    const cropModal = document.getElementById('cropModal');
    const cropImage = document.getElementById('cropImage');
    const cancelCrop = document.getElementById('cancelCrop');
    const confirmCrop = document.getElementById('confirmCrop');
    const form = document.getElementById('edit-service-form');
    const currentImageWrapper = document.getElementById('currentImageWrapper');
    const currentImage = document.getElementById('currentImage');

    let cropper;
    let croppedBlob = null;
    let imageChanged = false;

    cancelCrop.className = "btn-warning w-full rounded-lg px-4 py-2 md:w-auto";
    confirmCrop.className = "btn-primary w-full rounded-lg px-4 py-2 md:w-auto";

    const openCropper = file => {
        const reader = new FileReader();
        reader.onload = e => {
            cropImage.src = e.target.result;
            cropModal.classList.remove('hidden');
            if (cropper) cropper.destroy();
            cropper = new Cropper(cropImage, {aspectRatio: 1, viewMode: 1});
            croppedBlob = null;
        };
        reader.readAsDataURL(file);
    };

    const handleFileSelect = () => {
        if (!input.files.length) return;
        imageChanged = true;
        openCropper(input.files[0]);
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
        if (!cropper) return;
        cropper.getCroppedCanvas({width: 500, height: 500}).toBlob(blob => {
            croppedBlob = blob;
            const url = URL.createObjectURL(blob);
            currentImage.src = url;
            currentImageWrapper.classList.remove('hidden');

            const newFile = new File([blob], 'cropped_image.png', {type: 'image/png'});
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(newFile);
            input.files = dataTransfer.files;

            cropModal.classList.add('hidden');
            cropper.destroy();
            cropper = null;
        }, 'image/png');
    });

    form.addEventListener('submit', e => {
        e.preventDefault();
        loader.classList.remove('hidden');

        const formData = new FormData(form);

        // حذف فایل اصلی فقط اگر blob داریم
        if (croppedBlob) {
            formData.delete(input.name);
            formData.append(input.name, croppedBlob, 'cropped_image.png');
        }

        formData.forEach((value, key) => {
            if (key.startsWith('option-') || key.startsWith('schedule-')) {
                formData.delete(key);
            }
        });

        fetch(form.action, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
        })
            .then(async res => {
                const contentType = res.headers.get("content-type") || "";
                if (contentType.includes("application/json")) return res.json();
                else throw new Error("Redirecting to another page");
            })
            .then(data => {
                loader.classList.add('hidden');
                if (data.success) {
                    Swal.fire({
                        toast: true,
                        position: 'top-end',
                        icon: 'success',
                        title: 'عملیات با موفقیت انجام شد',
                        showConfirmButton: false,
                        timer: 2000,
                        timerProgressBar: true,
                    }).then(() => {
                        if (data.redirect_url) window.location.href = data.redirect_url;
                        else location.reload();
                    });
                } else {
                    Swal.fire({icon: 'error', title: 'خطا در ذخیره‌سازی', text: 'مشکلی پیش آمد. دوباره تلاش کنید.'});
                }
            })
            .catch(err => {
                loader.classList.add('hidden');
                if (err.message !== "Redirecting to another page") {
                    Swal.fire({icon: 'error', title: 'خطا در اتصال', text: 'ارتباط با سرور برقرار نشد.'});
                }
            });
    });

    function sendForm() {
        const formData = new FormData(form);

        // حذف فایل اصلی و جایگزین کردن با عکس کراپ شده
        formData.delete(input.name);
        if (croppedBlob) formData.append(input.name, croppedBlob, 'cropped_image.png');

        // حذف فیلدهای option و schedule در حالت edit
        formData.forEach((value, key) => {
            if (key.startsWith('option-') || key.startsWith('schedule-')) {
                formData.delete(key);
            }
        });

        fetch(form.action, {
            method: 'POST',
            body: formData,
            credentials: 'same-origin',
        })
            .then(async res => {
                const contentType = res.headers.get("content-type") || "";
                if (contentType.includes("application/json")) return res.json();
                else throw new Error("Redirecting to another page");
            })
            .then(data => {
                loader.classList.add('hidden');
                if (data.success) {
                    Swal.fire({
                        toast: true,
                        position: 'top-end',
                        icon: 'success',
                        title: 'عملیات با موفقیت انجام شد',
                        showConfirmButton: false,
                        timer: 2000,
                        timerProgressBar: true,
                    }).then(() => {
                        if (data.redirect_url) window.location.href = data.redirect_url;
                        else location.reload();
                    });
                } else {
                    Swal.fire({icon: 'error', title: 'خطا در ذخیره‌سازی', text: 'مشکلی پیش آمد. دوباره تلاش کنید.'});
                }
            })
            .catch(err => {
                loader.classList.add('hidden');
                if (err.message !== "Redirecting to another page") {
                    Swal.fire({icon: 'error', title: 'خطا در اتصال', text: 'ارتباط با سرور برقرار نشد.'});
                }
            });
    }
});
