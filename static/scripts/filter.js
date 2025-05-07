$(document).ready(function () {
    function getSelectedFilters(className) {
        let selected = [];
        $(className + ':checked').each(function () {
            selected.push($(this).val());
        });
        return selected.join(',');
    }

    function filterServices(page = 1, sortBy = null, removeSort = false) {
        let categories = getSelectedFilters('input[name="category-filter"]');
        let tags = getSelectedFilters('input[name="tags-filter"]');
        let professions = getSelectedFilters('input[name="professions-filter"]');
        let locations = getSelectedFilters('input[name="locations-filter"]');
        let available = $('input[name="available-filter"]:checked').val();
        let featured = $('input[name="featured-filter"]:checked').val();

        let filters = {page: page};

        if (categories) filters.category = categories;
        if (tags) filters.tag = tags;
        if (professions) filters.profession = professions;
        if (locations) filters.location = locations;
        if (available) filters.available = available;
        if (featured) filters.featured = featured;

        if (sortBy && !removeSort) {
            filters.sort_by = sortBy;
        } else if (!sortBy) {
            let currentSort = $('.sort-filter.active').data('sort');
            if (currentSort) filters.sort_by = currentSort;
        }

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

                let newUrl = '/services/';
                if (!$.isEmptyObject(filters)) newUrl += '?' + $.param(filters);
                history.pushState(null, '', newUrl);

                $('html, body').animate({scrollTop: 0}, 'slow');
            },
            error: function (err) {
                Swal.close();
                console.log('Error:', err);
            }
        });
    }


    function debounce(func, delay) {
        let timeout;
        return function (...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    }

    let debouncedFilter = debounce(filterServices, 500);

    $('input[name="category-filter"], input[name="tags-filter"], input[name="professions-filter"], input[name="locations-filter"], input[name="available-filter"], input[name="featured-filter"]').change(function () {
        debouncedFilter();
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
        professions: params.get('profession') ? params.get('v').split(',') : [],
        locations: params.get('location') ? params.get('location').split(',') : [],
        page: params.get('page') || 1
    };

    if (filters.sort_by)
        $(`.sort-filter[data-sort="${filters.sort_by}"]`).addClass('active text-red-500').removeClass('opacity-70');

    filters.categories.forEach(val => $(`input[name="category-filter"][value="${val}"]`).prop('checked', true));
    filters.tags.forEach(val => $(`input[name="tags-filter"][value="${val}"]`).prop('checked', true));
    filters.professions.forEach(val => $(`input[name="professions-filter"][value="${val}"]`).prop('checked', true));
    filters.locations.forEach(val => $(`input[name="locations-filter"][value="${val}"]`).prop('checked', true));

    filterServices(filters.page);
});