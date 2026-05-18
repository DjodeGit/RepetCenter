document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const tableBody = document.getElementById('table-body');
    const paginationContainer = document.getElementById('pagination-container');
    const globalLoader = document.getElementById('global-loader');
    const resetBtn = document.getElementById('btn-reset-filters');

    if (!searchInput || !tableBody || !paginationContainer) return;

    let searchTimeout;
    let currentPage = 1;
    let currentSearch = '';
    let isLoading = false;

    function buildUrl(page) {
        const params = new URLSearchParams();
        params.set('page', page);
        if (currentSearch && currentSearch.trim().length > 0) {
            params.set('search', currentSearch.trim());
        }
        return `${window.location.pathname}?${params.toString()}`;
    }

    function setLoading(loading) {
        isLoading = loading;
        if (globalLoader) {
            if (loading) globalLoader.classList.remove('hidden');
            else globalLoader.classList.add('hidden');
        }
    }

    function loadRows(page) {
        if (isLoading) return;
        currentPage = page;
        setLoading(true);

        const url = buildUrl(page);

        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        })
            .then(response => response.json())
            .then(data => {
                if (data.rows_html) tableBody.innerHTML = data.rows_html;
                if (data.pagination_html) paginationContainer.innerHTML = data.pagination_html;
                setLoading(false);
            })
            .catch(err => {
                console.error('Erreur loadRows:', err);
                setLoading(false);
            });
    }

    // Recherche avec debounce
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = window.setTimeout(() => {
            currentSearch = this.value;
            currentPage = 1;
            loadRows(1);
            if (resetBtn) {
                if (currentSearch.trim().length > 0) resetBtn.classList.remove('hidden');
                else resetBtn.classList.add('hidden');
            }
        }, 300);
    });

    // Reset filters
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            currentSearch = '';
            searchInput.value = '';
            resetBtn.classList.add('hidden');
            loadRows(1);
        });
    }

    // Pagination avec délégation d'événements
    paginationContainer.addEventListener('click', (e) => {
        const link = e.target.closest('a');
        if (!link) return;
        e.preventDefault();
        
        const url = new URL(link.href);
        const page = url.searchParams.get('page');
        if (page && !isNaN(parseInt(page))) {
            loadRows(parseInt(page));
        }
    });

    // Initialisation
    const urlParams = new URLSearchParams(window.location.search);
    const initialSearch = urlParams.get('search') || '';
    const initialPage = parseInt(urlParams.get('page') || '1', 10);

    if (initialSearch) {
        currentSearch = initialSearch;
        searchInput.value = initialSearch;
        if (resetBtn) resetBtn.classList.remove('hidden');
    }

    if (initialPage > 1) {
        loadRows(initialPage);
    }
});