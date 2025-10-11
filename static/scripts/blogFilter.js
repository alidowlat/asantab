$(document).ready(function () {
    let pendingFilters = {};

    function getSelectedFilters(className) {
        let selected = new Set();
        $(className + ':checked').each(function () {
            selected.add($(this).val());
        });
        return Array.from(selected).join(',');
    }

    function updatePendingFilters() {
        pendingFilters = {
            categories: getSelectedFilters('input[name="category-filter"]') || '',
            tags: getSelectedFilters('input[name="tags-filter"]') || '',
            search: $('input[name="search-filter"]').val() || $('input[name="search-filter-mobile"]').val() || ''
        };
    }

    function showBlogLoader() {
        let loaderHTML = '';
        for (let i = 0; i < 12; i++) {
            loaderHTML += `
                <div class="relative bg-muted rounded-xl overflow-hidden">
                    <div class="flex flex-col">
                        <div class="mb-4 p-2 lg:p-4 bg-secondary flex justify-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                 viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                                 class="lucide lucide-image-icon w-full h-auto max-w-50 max-h-50 text-text/60/10 animate-pulse">
                                <rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect>
                                <circle cx="9" cy="9" r="2"></circle>
                                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
                            </svg>
                        </div>
                        <div class="px-2 lg:px-4 flex flex-col justify-between gap-3 h-10 lg:h-12">
                            <div class="animate-pulse rounded-md bg-background h-full"></div>
                            <div class="animate-pulse rounded-md bg-background h-full"></div>
                        </div>
                        <div class="flex flex-col px-2 lg:px-4">
                            <div class="h-5 flex justify-end items-center">
                                <div class="animate-pulse rounded-md bg-background h-2 w-10"></div>
                            </div>
                            <div class="flex justify-end items-center">
                                <div class="animate-pulse rounded-md bg-background h-5 w-2/3"></div>
                            </div>
                            <div class="h-8 flex justify-center items-center">
                                <div class="animate-pulse rounded-md bg-background h-2 w-full"></div>
                            </div>
                        </div>
                    </div>
                </div>`;
        }
        $('#blog-list').html(loaderHTML);
        $('#pagination').empty();
    }

    function filterBlog(page = 1, sortBy = null, removeSort = false) {
        let filters = {page: page};

        if (pendingFilters.categories) filters.category = pendingFilters.categories;
        if (pendingFilters.tags) filters.tag = pendingFilters.tags;
        if (pendingFilters.search) filters.s = pendingFilters.search;

        if (sortBy && !removeSort) {
            filters.sort_by = sortBy;
        } else {
            let currentSort = $('.sort-filter.bg-primary\\/15').data('sort');
            filters.sort_by = currentSort || 'newest';
        }

        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });

        $.ajax({
            url: '/blog/',
            method: 'GET',
            data: filters,
            beforeSend: function () {
                showBlogLoader();
                Swal.fire({
                    title: 'در حال بارگذاری...',
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading()
                });
            },
            success: function (data) {
                setTimeout(() => {
                    $('#post-list').html($(data).find('#post-list').html());
                    $('#pagination').html($(data).find('#pagination').html());
                    Swal.close();

                    let query = $.param(filters);
                    let newUrl = query ? `/blog/?${query}` : '/blog/';
                    history.pushState(null, '', newUrl);
                    $('html, body').animate({scrollTop: 0}, 'slow');
                });
            },
            error: function (err) {
                Swal.close();
            }
        });
    }

    $('#apply-filters-btn, #apply-filters-btn-mobile').click(function () {
        updatePendingFilters();
        filterBlog(1);
        $('#filter-drawer').addClass('translate-y-full').attr('aria-hidden', 'true');
    });

    $(document).on('change', 'input[name$="-filter"]', function () {
        let name = $(this).attr('name');
        let val = $(this).val();
        let isChecked = $(this).prop('checked');
        $(`input[name="${name}"][value="${val}"]`).not(this).prop('checked', isChecked);
        updatePendingFilters();
    });

    $(document).on('click', '.sort-filter', function () {
        const sortBy = $(this).data('sort');
        window.toggleSortFilter(sortBy);
    });

    window.toggleSortFilter = function (sortBy) {
        const target = $(`.sort-filter[data-sort="${sortBy}"]`);
        const isActive = target.hasClass('bg-primary/15');

        $('.sort-filter').removeClass('bg-primary/15 text-primary').addClass('opacity-70');

        if (isActive) {
            filterBlog(1, null, true);
        } else {
            target.addClass('bg-primary/15 text-primary').removeClass('opacity-70');
            filterBlog(1, sortBy);
        }
    };

    $(document).on('click', '#pagination a', function (e) {
        e.preventDefault();
        let page = $(this).attr('href').split('page=')[1].split('&')[0];
        filterBlog(page);
    });

    let params = new URLSearchParams(window.location.search);
    let filters = {
        sort_by: params.get('sort_by') || 'newest',
        categories: params.get('category') ? params.get('category').split(',') : [],
        tags: params.get('tag') ? params.get('tag').split(',') : [],
        search: params.get('s') || '',
        page: params.get('page') ? parseInt(params.get('page')) : 1
    };

    if (filters.sort_by) {
        const target = $(`.sort-filter[data-sort="${filters.sort_by}"]`);
        target.addClass('bg-primary/15 text-primary').removeClass('opacity-70');
        $(`.sort-radio-mobile[data-sort="${filters.sort_by}"]`).prop('checked', true);
    }

    function syncCheck(name, val) {
        $(`input[name="${name}"][value="${val}"]`).prop('checked', true);
    }

    filters.categories.forEach(val => syncCheck('category-filter', val));
    filters.tags.forEach(val => syncCheck('tags-filter', val));

    if (filters.search) $('input[name="search-filter"], input[name="search-filter-mobile"]').val(filters.search);

    $('#apply-sort-btn-mobile').click(function () {
        const selected = $('.sort-radio-mobile:checked');
        const sortBy = selected.data('sort');
        $('.sort-filter').removeClass('bg-primary/15 text-primary').addClass('opacity-70');
        if (sortBy) {
            const target = $(`.sort-filter[data-sort="${sortBy}"]`);
            target.addClass('bg-primary/15 text-primary').removeClass('opacity-70');
        }
        filterBlog(1, sortBy);
    });

    $('#clear-filters-btn, #clear-filters-btn-mob').click(function () {
        $('input[name$="-filter"]').prop('checked', false);
        $('input[name="search-filter"]').val('');
        $('input[name="search-filter-mobile"]').val('');
        updatePendingFilters();
        $('#filter-drawer').addClass('translate-y-full').attr('aria-hidden', 'true');
        filterBlog(1);
    });

    updatePendingFilters();
    filterBlog(filters.page, filters.sort_by);
});
