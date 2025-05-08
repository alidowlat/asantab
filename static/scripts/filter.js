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
            professions: getSelectedFilters('input[name="professions-filter"]') || '',
            locations: getSelectedFilters('input[name="locations-filter"]') || '',
            available: $('input[name="available-filter"]:checked').val() || '',
            featured: $('input[name="featured-filter"]:checked').val() || ''
        };
    }

    function filterServices(page = 1, sortBy = null, removeSort = false) {
        let filters = {page: page};

        if (pendingFilters.categories) filters.category = pendingFilters.categories;
        else delete filters.category;

        if (pendingFilters.tags) filters.tag = pendingFilters.tags;
        else delete filters.tag;

        if (pendingFilters.professions) filters.profession = pendingFilters.professions;
        else delete filters.profession;

        if (pendingFilters.locations) filters.location = pendingFilters.locations;
        else delete filters.location;

        if (pendingFilters.available) filters.available = pendingFilters.available;
        else delete filters.available;

        if (pendingFilters.featured) filters.featured = pendingFilters.featured;
        else delete filters.featured;

        if (sortBy && !removeSort) {
            filters.sort_by = sortBy;
        } else if (!sortBy) {
            let currentSort = $('.sort-filter.active').data('sort');
            if (currentSort) filters.sort_by = currentSort;
        }

        // Clean up empty filters before sending the request
        Object.keys(filters).forEach(key => {
            if (filters[key] === '' || filters[key] == null) {
                delete filters[key];
            }
        });

        $.ajax({
            url: '/services/',
            method: 'GET',
            data: filters,
            beforeSend: function () {
                Swal.fire({
                    title: 'لطفا صبر کنید...',
                    html: 'در حال بارگزاری...',
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading()
                });
            },
            success: function (data) {
                $('#service-list').html($(data).find('#service-list').html());
                $('#pagination').html($(data).find('#pagination').html());
                Swal.close();

                let baseUrl = '/services/';
                let query = $.param(filters);
                let newUrl = query ? `${baseUrl}?${query}` : baseUrl;

                history.pushState(null, '', newUrl);
                $('html, body').animate({scrollTop: 0}, 'slow');
            },
            error: function (err) {
                Swal.close();
                console.log('Error:', err);
            }
        });
    }

    $('#apply-filters-btn').click(function () {
        updatePendingFilters();
        filterServices(1);
    });

    $('#apply-filters-btn-mobile').click(function () {
        updatePendingFilters();
        filterServices(1);
        $('#filter-drawer').addClass('translate-y-full').attr('aria-hidden', 'true');
    });

    $(document).on('change', 'input[name$="-filter"]', function () {
        let name = $(this).attr('name');
        let val = $(this).val();
        let isChecked = $(this).prop('checked');

        // sync all with the same name and value
        $(`input[name="${name}"][value="${val}"]`).not(this).prop('checked', isChecked);

        updatePendingFilters();
    });


    window.toggleSortFilter = function (sortBy) {
        let current = $(`.sort-filter[data-sort="${sortBy}"]`).hasClass('active');
        $('.sort-filter').removeClass('active text-red-500').addClass('opacity-70');
        if (current) {
            filterServices(1, null, true);
        } else {
            $(`.sort-filter[data-sort="${sortBy}"]`).addClass('active text-red-500').removeClass('opacity-70');
            filterServices(1, sortBy);
        }
    };

    $(document).on('click', '#pagination a', function (e) {
        e.preventDefault();
        let page = $(this).attr('href').split('page=')[1].split('&')[0];
        filterServices(page);
    });

    let params = new URLSearchParams(window.location.search);
    let filters = {
        sort_by: params.get('sort_by'),
        categories: params.get('category') ? params.get('category').split(',') : [],
        tags: params.get('tag') ? params.get('tag').split(',') : [],
        professions: params.get('profession') ? params.get('profession').split(',') : [],
        locations: params.get('location') ? params.get('location').split(',') : [],
        available: params.get('available') || '',
        featured: params.get('featured') || '',
        page: params.get('page') ? parseInt(params.get('page')) : 1
    };

    if (filters.sort_by)
        $(`.sort-filter[data-sort="${filters.sort_by}"]`).addClass('active text-red-500').removeClass('opacity-70');

    function syncCheck(name, val) {
        $(`input[name="${name}"][value="${val}"]`).each(function () {
            $(this).prop('checked', true);
        });
    }

    filters.categories.forEach(val => syncCheck('category-filter', val));
    filters.tags.forEach(val => syncCheck('tags-filter', val));
    filters.professions.forEach(val => syncCheck('professions-filter', val));
    filters.locations.forEach(val => syncCheck('locations-filter', val));
    if (filters.available) syncCheck('available-filter', filters.available);
    if (filters.featured) syncCheck('featured-filter', filters.featured);

    updatePendingFilters();
    filterServices(filters.page);
});

// document.addEventListener('DOMContentLoaded', function () {
//     const drawer = document.getElementById("filter-drawer");
//     const toggleBtn = document.getElementById("filter-toggle-btn");
//     const applyBtn = document.getElementById("apply-filters-btn");
//
//     function openDrawer() {
//         drawer.classList.remove("translate-y-full");
//         drawer.setAttribute("aria-hidden", "false");
//     }
//
//     function closeDrawer() {
//         drawer.classList.add("translate-y-full");
//         drawer.setAttribute("aria-hidden", "true");
//     }
//
//     toggleBtn?.addEventListener("click", openDrawer);
//
//     applyBtn?.addEventListener("click", function () {
//         closeDrawer();
//     });
//
//     const filterToggleBtn = document.getElementById("filter-toggle-btn");
//
//     if (filterToggleBtn) {
//         filterToggleBtn.addEventListener("click", openDrawer);  // وقتی فیلتر باز میشه
//     }
// });