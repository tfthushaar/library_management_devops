const addBookForm = document.getElementById("add-book-form");
const borrowForm = document.getElementById("borrow-form");
const borrowBookSelect = document.getElementById("borrow-book-id");
const memberNameInput = document.getElementById("member-name");
const searchInput = document.getElementById("search-query");
const searchButton = document.getElementById("search-button");
const resetButton = document.getElementById("reset-button");
const messageBox = document.getElementById("message");
const catalogBody = document.getElementById("catalog-body");
const loanList = document.getElementById("loan-list");

const statTotalBooks = document.getElementById("stat-total-books");
const statAvailableCopies = document.getElementById("stat-available-copies");
const statBorrowedCopies = document.getElementById("stat-borrowed-copies");
const statActiveMembers = document.getElementById("stat-active-members");

function setMessage(text, variant) {
  messageBox.textContent = text;
  messageBox.className = `message ${variant}`;
}

async function requestJson(url, options = {}) {
  try {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
      },
      ...options,
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "The request could not be completed.");
    }
    return payload;
  } catch (error) {
    setMessage(error.message, "error");
    throw error;
  }
}

function renderSummary(summary) {
  statTotalBooks.textContent = summary.total_books;
  statAvailableCopies.textContent = summary.available_copies;
  statBorrowedCopies.textContent = summary.borrowed_copies;
  statActiveMembers.textContent = summary.active_members;
}

function renderBorrowOptions(books) {
  borrowBookSelect.innerHTML = "";

  books.forEach((book) => {
    const option = document.createElement("option");
    option.value = book.id;
    option.textContent = `${book.title} (${book.available_copies}/${book.total_copies} available)`;
    option.disabled = book.available_copies === 0;
    borrowBookSelect.appendChild(option);
  });
}

function renderLoans(loans) {
  if (loans.length === 0) {
    loanList.innerHTML =
      '<div class="empty-state">No active loans yet. Issue a book to see live circulation data here.</div>';
    return;
  }

  loanList.innerHTML = loans
    .map(
      (loan) => `
        <article class="loan-card">
          <strong>${loan.book_title}</strong>
          <span>${loan.book_author}</span>
          <span>Issued to ${loan.member_name}</span>
          <span>${new Date(loan.issued_at).toLocaleString()}</span>
        </article>
      `,
    )
    .join("");
}

function renderCatalog(books) {
  if (books.length === 0) {
    catalogBody.innerHTML = `
      <tr>
        <td colspan="7" class="empty-state">No books matched your search query.</td>
      </tr>
    `;
    return;
  }

  catalogBody.innerHTML = books
    .map(
      (book) => `
        <tr>
          <td>${book.title}</td>
          <td>${book.author}</td>
          <td>${book.category}</td>
          <td>${book.isbn}</td>
          <td>${book.available_copies}/${book.total_copies}</td>
          <td>
            <span class="status-chip ${book.available_copies > 0 ? "available" : "issued"}">${book.status}</span>
          </td>
          <td>
            <button
              type="button"
              class="action-button ${book.available_copies === book.total_copies ? "ghost-button" : ""}"
              data-action="${book.available_copies === book.total_copies ? "borrow" : "return"}"
              data-book-id="${book.id}"
            >
              ${book.available_copies === book.total_copies ? "Issue" : "Return"}
            </button>
          </td>
        </tr>
      `,
    )
    .join("");
}

async function refreshDashboard(query = "") {
  const [summary, catalog, loans] = await Promise.all([
    requestJson("/api/summary"),
    requestJson(`/api/books${query ? `?q=${encodeURIComponent(query)}` : ""}`),
    requestJson("/api/loans"),
  ]);

  renderSummary(summary);
  renderCatalog(catalog.books);
  renderLoans(loans.loans);

  const fullCatalog = query ? (await requestJson("/api/books")).books : catalog.books;
  renderBorrowOptions(fullCatalog);
}

addBookForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    title: document.getElementById("title").value.trim(),
    author: document.getElementById("author").value.trim(),
    isbn: document.getElementById("isbn").value.trim(),
    category: document.getElementById("category").value.trim(),
    copies: document.getElementById("copies").value,
  };

  await requestJson("/api/books", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  addBookForm.reset();
  document.getElementById("copies").value = 2;
  setMessage("Book added successfully. Re-run OWASP ZAP after deployment to verify the updated portal.", "success");
  await refreshDashboard(searchInput.value.trim());
});

borrowForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const bookId = borrowBookSelect.value;
  const memberName = memberNameInput.value.trim();

  if (!bookId) {
    setMessage("Select a book before issuing it.", "error");
    return;
  }

  const payload = await requestJson(`/api/books/${bookId}/borrow`, {
    method: "POST",
    body: JSON.stringify({ member_name: memberName }),
  });

  borrowForm.reset();
  setMessage(payload.message, "success");
  await refreshDashboard(searchInput.value.trim());
});

searchButton.addEventListener("click", async () => {
  const query = searchInput.value.trim();
  await refreshDashboard(query);
  setMessage(query ? `Filtered catalog using "${query}".` : "Showing the full catalog.", "info");
});

resetButton.addEventListener("click", async () => {
  searchInput.value = "";
  await refreshDashboard();
  setMessage("Search cleared. Full catalog restored.", "info");
});

catalogBody.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) {
    return;
  }

  const bookId = button.dataset.bookId;
  const action = button.dataset.action;

  if (action === "borrow") {
    borrowBookSelect.value = bookId;
    memberNameInput.focus();
    setMessage("Enter a member name in the issue form to complete the loan.", "info");
    return;
  }

  const payload = await requestJson(`/api/books/${bookId}/return`, {
    method: "POST",
    body: JSON.stringify({}),
  });
  setMessage(payload.message, "success");
  await refreshDashboard(searchInput.value.trim());
});

document.addEventListener("DOMContentLoaded", async () => {
  try {
    await refreshDashboard();
  } catch (error) {
    setMessage("The portal could not load its initial data.", "error");
  }
});
