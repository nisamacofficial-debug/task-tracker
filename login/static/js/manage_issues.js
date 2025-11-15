// manage_issues.js
(function () {
  // --- CSRF helper ---
  function getCookie(name) {
    if (!document.cookie) return null;
    const cookies = document.cookie.split(';').map(c => c.trim());
    for (const c of cookies) {
      if (c.startsWith(name + '=')) return decodeURIComponent(c.split('=')[1]);
    }
    return null;
  }
  const csrftoken = getCookie('csrftoken');

  function jsonPost(url, data) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify(data || {})
    }).then(r => r.json());
  }

  // --- DOM references ---
  const statusFilter = document.getElementById('statusFilter');
  const tagFilter = document.getElementById('tagFilter');
  const searchInput = document.getElementById('searchInput');
  const clearBtn = document.getElementById('clearFilters');

  const commentsPanel = document.getElementById('commentsPanel');
  const commentsList = document.getElementById('commentsList');
  const closePanelBtn = document.getElementById('closePanel');
  const commentForm = document.getElementById('commentForm');
  const newCommentInput = document.getElementById('newComment');

  const toastEl = document.getElementById('deleteToast');
  const bootstrapToast = new bootstrap.Toast(toastEl, { delay: 3000 });

  let currentIssueId = null;

  // --- Filtering ---
  function matchesFilter(row) {
    const title = row.querySelector('.title-cell')?.innerText.toLowerCase() || '';
    const desc = row.querySelector('.desc-cell')?.innerText.toLowerCase() || '';
    const statusText = row.querySelector('.status-text')?.innerText.toLowerCase() || '';
    const tagText = row.querySelector('.tag-cell')?.innerText.toLowerCase() || '';

    const s = statusFilter.value.trim().toLowerCase();
    const t = tagFilter.value.trim().toLowerCase();
    const q = searchInput.value.trim().toLowerCase();

    const statusOk = !s || statusText.includes(s);
    const tagOk = !t || tagText.includes(t);
    const queryOk = !q || title.includes(q) || desc.includes(q);

    return statusOk && tagOk && queryOk;
  }

  function applyFilters() {
    const rows = document.querySelectorAll('#issuesTable tbody tr[data-issue-id]');
    rows.forEach(row => {
      row.style.display = matchesFilter(row) ? '' : 'none';
    });
  }

  [statusFilter, tagFilter, searchInput].forEach(el => {
    if (!el) return;
    el.addEventListener('input', applyFilters);
    el.addEventListener('change', applyFilters);
  });

  clearBtn.addEventListener('click', () => {
    statusFilter.value = '';
    tagFilter.value = '';
    searchInput.value = '';
    applyFilters();
  });

  // --- Inline status change ---
  document.addEventListener('click', function (e) {
    const statusTextEl = e.target.closest('.status-text');
    if (statusTextEl) {
      const cell = statusTextEl.closest('.status-cell');
      if (!cell) return;
      const select = cell.querySelector('.status-select');
      statusTextEl.classList.add('d-none');
      select.classList.remove('d-none');
      select.focus();
    }
  });

  document.addEventListener('change', function (e) {
    const select = e.target.closest('.status-select');
    if (!select) return;
    const cell = select.closest('.status-cell');
    const issueId = cell.getAttribute('data-issue-id');
    const newStatus = select.value;

    jsonPost(`/update-status/${issueId}/`, { status: newStatus })
      .then(data => {
        if (data && data.success) {
          const textEl = cell.querySelector('.status-text');
          let badgeClass = 'bg-secondary';
          if (newStatus === 'closed') badgeClass = 'bg-success';
          else if (newStatus === 'in_progress') badgeClass = 'bg-warning text-dark';
          textEl.innerHTML = `<span class="badge ${badgeClass}">${newStatus.replace('_',' ').toUpperCase()}</span>`;
        } else {
          alert('Failed to update status.');
        }
      })
      .catch(() => alert('Error updating status.'))
      .finally(() => {
        select.classList.add('d-none');
        cell.querySelector('.status-text').classList.remove('d-none');
      });
  });

  document.addEventListener('blur', function(e) {
    const sel = e.target.closest('.status-select');
    if (!sel) return;
    setTimeout(() => {
      sel.classList.add('d-none');
      const text = sel.closest('.status-cell').querySelector('.status-text');
      if (text) text.classList.remove('d-none');
    }, 100);
  }, true);

  // --- Comments Panel ---
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.view-comments');
    if (!btn) return;
    currentIssueId = btn.getAttribute('data-issue-id');
    commentsPanel.classList.add('active');
    commentsList.innerHTML = '<p class="text-muted">Loading...</p>';

    fetch(`/issues/${currentIssueId}/comments/`)
      .then(r => r.json())
      .then(data => {
        if (data.comments && data.comments.length) {
          commentsList.innerHTML = data.comments.map(c => `
            <div class="comment-box">
              <strong>${c.user}</strong> <small class="text-muted"> ${c.created_at} </small>
              <p style="margin:.35rem 0 0;">${c.text}</p>
            </div>
          `).join('');
        } else {
          commentsList.innerHTML = '<p class="text-muted">No comments yet.</p>';
        }
      })
      .catch(() => commentsList.innerHTML = '<p class="text-danger">Failed to load comments.</p>');
  });

  closePanelBtn.addEventListener('click', () => {
    commentsPanel.classList.remove('active');
    currentIssueId = null;
  });

  document.addEventListener('click', (e) => {
    if (!commentsPanel.classList.contains('active')) return;
    const inside = commentsPanel.contains(e.target) || e.target.closest('.view-comments');
    if (!inside) {
      commentsPanel.classList.remove('active');
      currentIssueId = null;
    }
  });

  commentForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const text = newCommentInput.value.trim();
    if (!text) return alert('Please enter a comment.');
    if (!currentIssueId) return alert('Select an issue first.');

    jsonPost(`/add-comment/${currentIssueId}/`, { text })
      .then(data => {
        if (data && data.success) {
          const c = data.comment;
          commentsList.insertAdjacentHTML('beforeend', `
            <div class="comment-box">
              <strong>${c.user}</strong> <small class="text-muted"> ${c.created_at} </small>
              <p style="margin:.35rem 0 0;">${c.text}</p>
            </div>
          `);
          newCommentInput.value = '';
        } else alert('Failed to add comment.');
      })
      .catch(() => alert('Error adding comment.'));
  });

  // --- Delete Issue ---
  document.addEventListener('click', function (e) {
    const delBtn = e.target.closest('.delete-issue');
    if (!delBtn) return;
    const issueId = delBtn.getAttribute('data-issue-id');
    if (!confirm('Are you sure you want to delete issue #' + issueId + '?')) return;

    jsonPost(`/delete-issue/${issueId}/`, {})
      .then(data => {
        if (data && data.success) {
          const row = document.querySelector(`#issuesTable tbody tr[data-issue-id="${issueId}"]`);
          if (row) row.remove();
          bootstrapToast.show();
        } else alert('Failed to delete: ' + (data.error || 'unknown'));
      })
      .catch(() => alert('Error deleting issue.'));
  });

  // --- Initial filter apply ---
  document.addEventListener('DOMContentLoaded', applyFilters);
})();
