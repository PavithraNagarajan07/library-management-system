let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
        window.location.href = 'index.html';
        return;
    }
    currentUser = JSON.parse(userStr);
    setupUI();
    loadDashboard();

    // Global Event Listeners
    document.getElementById('logoutBtn').addEventListener('click', () => api.logout());
    document.querySelectorAll('.nav-link[data-view]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            switchView(e.currentTarget.dataset.view);
        });
    });

    // Book Search
    document.getElementById('bookSearch')?.addEventListener('input', debounce(loadCatalog, 500));

    // Add Book Modal
    const addBookBtn = document.getElementById('addBookBtn');
    if (addBookBtn) {
        addBookBtn.onclick = () => {
            document.getElementById('modalTitle').innerText = 'Add New Book';
            document.getElementById('bookForm').reset();
            openModal('bookModal');
        };
    }

    // Bulk Upload
    const bulkBtn = document.getElementById('bulkUploadBtn');
    const bulkInput = document.getElementById('bulkFileInput');
    if (bulkBtn && bulkInput) {
        bulkBtn.onclick = () => bulkInput.click();
        bulkInput.onchange = handleBulkUpload;
    }

    document.getElementById('bookForm')?.addEventListener('submit', handleBookSubmit);
});

function setupUI() {
    document.getElementById('userName').innerText = currentUser.full_name;
    document.getElementById('userRole').innerText = currentUser.role.toUpperCase();

    if (currentUser.role === 'admin') {
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'block');
        document.getElementById('adminStats').style.display = 'grid';
    }
}

async function switchView(viewName) {
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    document.querySelector(`.nav-link[data-view="${viewName}"]`).classList.add('active');

    // Hide all views
    document.querySelectorAll('.view-section').forEach(s => s.style.display = 'none');

    const viewTitle = document.getElementById('viewTitle');

    if (viewName === 'overview') {
        viewTitle.innerText = 'Dashboard Overview';
        document.getElementById('view-overview').style.display = 'block';
        loadDashboard();
    } else if (viewName === 'catalog') {
        viewTitle.innerText = 'Book Catalog';
        document.getElementById('view-catalog').style.display = 'block';
        loadCatalog();
    } else if (viewName === 'my-books') {
        viewTitle.innerText = 'My Borrows';
        document.getElementById('view-overview').style.display = 'block'; // Reuse table view
        loadMyBorrows();
    } else if (viewName === 'audit-logs') {
        viewTitle.innerText = 'System Audit Logs';
        document.getElementById('view-overview').style.display = 'block';
        loadAuditLogs();
    }
}

async function loadDashboard() {
    if (currentUser.role === 'admin') {
        const stats = await api.request('/dashboard/admin');
        document.getElementById('stat-total-books').innerText = stats.total_books;
        document.getElementById('stat-active-members').innerText = stats.active_members;
        document.getElementById('stat-books-issued').innerText = stats.books_issued;
        document.getElementById('stat-overdue').innerText = stats.overdue_books;

        loadRecentBorrowsAdmin();
    } else {
        loadRecentBorrowsMember();
    }
}

async function loadCatalog() {
    const search = document.getElementById('bookSearch').value;
    const books = await api.request(`/books/?search=${search}`);
    const grid = document.getElementById('bookGrid');
    grid.innerHTML = '';

    books.forEach(book => {
        const card = document.createElement('div');
        card.className = 'card';
        card.style.padding = '1.5rem';
        card.innerHTML = `
            <div style="display: flex; gap: 1rem;">
                <div style="width: 80px; height: 120px; background: #f1f5f9; border-radius: 4px; display: flex; align-items: center; justify-content: center;">
                    <i class="fas fa-book fa-2x" style="color: #cbd5e1;"></i>
                </div>
                <div style="flex-grow: 1;">
                    <h4 style="font-size: 1.1rem; margin-bottom: 0.25rem;">${book.title}</h4>
                    <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 0.5rem;">${book.author}</p>
                    <div style="margin-bottom: 1rem;">
                        <span class="badge badge-success">${book.category}</span>
                        <span class="badge" style="background:#f1f5f9; color: #475569;">${book.available_copies}/${book.total_copies} available</span>
                    </div>
                    <button class="btn btn-primary" style="width: auto; padding: 0.5rem 1rem;" onclick="borrowBook(${book.id}, '${book.title}')" ${book.available_copies === 0 ? 'disabled' : ''}>
                        ${book.available_copies === 0 ? 'Reserve' : 'Borrow'}
                    </button>
                </div>
            </div>
            <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--border-color); font-size: 0.75rem; color: var(--text-muted);">
                ISBN: ${book.isbn} • Published: ${book.year}
            </div>
        `;
        grid.appendChild(card);
    });
}

async function borrowBook(bookId, title) {
    if (!confirm(`Borrow "${title}"?`)) return;
    try {
        await api.request('/borrows/request', {
            method: 'POST',
            body: JSON.stringify({ book_id: bookId })
        });
        alert('Book borrowed successfully!');
        loadCatalog();
    } catch (error) {
        alert(error.message);
    }
}

async function loadRecentBorrowsAdmin() {
    const borrows = await api.request('/borrows/all');
    renderBorrowsTable(borrows, true);
}

async function loadMyBorrows() {
    const borrows = await api.request('/borrows/my-history');
    renderBorrowsTable(borrows, false);
}

async function loadAuditLogs() {
    const logs = await api.request('/dashboard/audit-logs');
    const header = document.getElementById('tableHeader');
    const body = document.getElementById('tableBody');

    header.innerHTML = `
        <th>Timestamp</th>
        <th>Admin ID</th>
        <th>Action</th>
        <th>Target</th>
    `;

    body.innerHTML = '';
    logs.forEach(log => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(log.timestamp).toLocaleString()}</td>
            <td>Admin #${log.admin_id}</td>
            <td><strong>${log.action}</strong></td>
            <td>${log.target_type} #${log.target_id}</td>
        `;
        body.appendChild(tr);
    });
}

function renderBorrowsTable(borrows, isAdmin) {
    const header = document.getElementById('tableHeader');
    const body = document.getElementById('tableBody');

    header.innerHTML = `
        <th>Book Title</th>
        ${isAdmin ? '<th>Member</th>' : ''}
        <th>Due Date</th>
        <th>Status</th>
        <th>Fine</th>
        <th>Actions</th>
    `;

    body.innerHTML = '';
    borrows.forEach(b => {
        const tr = document.createElement('tr');
        const statusClass = b.status === 'borrowed' ? 'badge-warning' : b.status === 'returned' ? 'badge-success' : 'badge-danger';

        tr.innerHTML = `
            <td><strong>${b.book.title}</strong><br><small>${b.book.isbn}</small></td>
            ${isAdmin ? `<td>${b.user_id}</td>` : ''}
            <td>${new Date(b.due_date).toLocaleDateString()}</td>
            <td><span class="badge ${statusClass}">${b.status}</span></td>
            <td>$${b.fine_amount.toFixed(2)}</td>
            <td>
                ${isAdmin && b.status !== 'returned' ? `<button class="btn" style="width:auto; padding:0.25rem 0.5rem; background:#2563eb; color:white;" onclick="returnBook(${b.id})">Return</button>` : '-'}
            </td>
        `;
        body.appendChild(tr);
    });
}

async function returnBook(borrowId) {
    if (!confirm('Mark this book as returned?')) return;
    try {
        await api.request(`/borrows/${borrowId}/return`, { method: 'POST' });
        loadDashboard();
    } catch (error) {
        alert(error.message);
    }
}

async function handleBookSubmit(e) {
    e.preventDefault();
    const formData = {
        isbn: document.getElementById('isbn').value,
        title: document.getElementById('title').value,
        author: document.getElementById('author').value,
        publisher: document.getElementById('publisher').value,
        category: document.getElementById('category').value,
        edition: document.getElementById('edition').value,
        year: parseInt(document.getElementById('year').value),
        total_copies: parseInt(document.getElementById('total_copies').value),
        available_copies: parseInt(document.getElementById('total_copies').value)
    };

    try {
        await api.request('/books/', {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        closeModal('bookModal');
        loadCatalog();
    } catch (error) {
        alert(error.message);
    }
}

async function handleBulkUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/books/bulk-upload`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
            body: formData
        });
        const data = await response.json();
        alert(data.message);
        loadCatalog();
    } catch (error) {
        alert(error.message);
    }
}

// Helpers
function openModal(id) { document.getElementById(id).style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
