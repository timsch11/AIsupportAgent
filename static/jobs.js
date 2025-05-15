// Global emails array - will be populated from the API
let emails = [];

// Current page and items per page for pagination
let currentPage = 1;
const itemsPerPage = 5;

// Fetch emails from the API
async function fetchEmails() {
    try {
        const response = await fetch('/api/emails');
        const data = await response.json();
        
        if (data.success) {
            // Transform the API response to match our expected format
            emails = data.emails.map((email, index) => ({
                id: index + 1,
                sender: {
                    name: email.sender.split('<')[0].trim() || 'Unknown',
                    email: (email.sender.match(/<(.+?)>/) || ['', email.sender])[1]
                },
                subject: email.subject || 'No Subject',
                preview: email.content || 'No content',
                timestamp: new Date().toISOString(), // Use current time if not provided
                tags: [],
                unread: true,
                rawContent: email.content // Store the full content for analysis
            }));
            
            renderEmails(1);
        } else {
            showToast('Failed to load emails: ' + data.message);
        }
    } catch (error) {
        console.error('Error fetching emails:', error);
        showToast('Failed to load emails');
    }
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const isToday = date.toDateString() === now.toDateString();
    
    if (isToday) {
        return `Today at ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    }
    
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (date.toDateString() === yesterday.toDateString()) {
        return `Yesterday at ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    }
    
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Function to render the email list
function renderEmails(page = 1) {
    const emailList = document.getElementById('email-list');
    emailList.innerHTML = '';
    
    // Calculate pagination indexes
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, emails.length);
    
    // Check if there are no emails
    if (emails.length === 0) {
        emailList.innerHTML = `
            <div class="empty-state">
                <h3>No emails found</h3>
                <p>Your inbox is empty or no emails match your search criteria.</p>
            </div>
        `;
        return;
    }
    
    // Display emails for the current page
    for (let i = startIndex; i < endIndex; i++) {
        const email = emails[i];
        const emailElement = document.createElement('div');
        emailElement.className = `email-card ${email.unread ? 'unread' : ''}`;
        emailElement.setAttribute('data-email-id', email.id);
        
        emailElement.innerHTML = `
            <div class="email-header">
                <div class="sender-info">
                    <span class="sender-name">${email.sender.name}</span>
                    <span class="sender-email">${email.sender.email}</span>
                </div>
                <span class="email-timestamp">${formatDate(email.timestamp)}</span>
            </div>
            <h3 class="email-subject">${email.subject}</h3>
            <div class="email-preview">${email.preview}</div>
            <div class="email-footer">
                <div class="email-tags">
                    ${email.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
                <button class="analyze-btn" data-email-id="${email.id}">Analyze Email</button>
            </div>
        `;
        
        emailList.appendChild(emailElement);
    }
    
    // Set up analyze button click handlers
    document.querySelectorAll('.analyze-btn').forEach(button => {
        button.addEventListener('click', handleAnalyzeClick);
    });
    
    renderPagination();
}

// Function to render pagination controls
function renderPagination() {
    const paginationElement = document.getElementById('pagination');
    paginationElement.innerHTML = '';
    
    const totalPages = Math.ceil(emails.length / itemsPerPage);
    
    // Only show pagination if there's more than one page
    if (totalPages <= 1) {
        return;
    }
    
    // Previous button
    const prevButton = document.createElement('button');
    prevButton.textContent = '←';
    prevButton.disabled = currentPage === 1;
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderEmails(currentPage);
        }
    });
    paginationElement.appendChild(prevButton);
    
    // Page number buttons
    for (let i = 1; i <= totalPages; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === currentPage ? 'active' : '';
        pageButton.addEventListener('click', () => {
            currentPage = i;
            renderEmails(currentPage);
        });
        paginationElement.appendChild(pageButton);
    }
    
    // Next button
    const nextButton = document.createElement('button');
    nextButton.textContent = '→';
    nextButton.disabled = currentPage === totalPages;
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderEmails(currentPage);
        }
    });
    paginationElement.appendChild(nextButton);
}

// Handle email analysis button click
async function handleAnalyzeClick(event) {
    const button = event.currentTarget;
    const emailId = parseInt(button.getAttribute('data-email-id'));
    const emailCard = document.querySelector(`.email-card[data-email-id="${emailId}"]`);
    
    // Find the email data
    const emailData = emails.find(email => email.id === emailId);
    if (!emailData) {
        showToast('Email not found');
        return;
    }
    
    // Show loading state
    button.innerHTML = 'Analyzing <span class="loading"></span>';
    emailCard.classList.add('analyzing');
    
    try {
        // Call the analysis API
        const response = await fetch('/api/analyze-email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content: emailData.rawContent })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Store analysis results in the email object for later use
            emailData.analysisResult = data;
            
            // Add the category and username as tags if they exist
            if (data.Kategorie) {
                if (!emailData.tags.includes(data.Kategorie)) {
                    emailData.tags.push(data.Kategorie);
                }
            }
            
            if (data.Benutzername) {
                if (!emailData.tags.includes(data.Benutzername)) {
                    emailData.tags.push(data.Benutzername);
                }
            }
            
            button.innerHTML = 'Analysis Complete';
            emailCard.classList.remove('analyzing');
            
            // Mark as read if it was unread
            if (emailCard.classList.contains('unread')) {
                emailCard.classList.remove('unread');
                emailData.unread = false;
            }
            
            // Update the tags display
            const tagsContainer = emailCard.querySelector('.email-tags');
            tagsContainer.innerHTML = emailData.tags.map(tag => `<span class="tag">${tag}</span>`).join('');
            
            // Add execute action button if we have both category and username
            if (data.Kategorie && data.Benutzername) {
                const emailFooter = emailCard.querySelector('.email-footer');
                
                // Check if button already exists
                let actionButton = emailFooter.querySelector('.action-btn');
                if (!actionButton) {
                    actionButton = document.createElement('button');
                    actionButton.className = 'action-btn';
                    actionButton.setAttribute('data-email-id', emailId);
                    actionButton.addEventListener('click', handleExecuteAction);
                    emailFooter.appendChild(actionButton);
                }
                
                actionButton.textContent = `Execute: ${data.Kategorie}`;
            }
            
            // Show editable toast notification with analysis results
            showEditableToast(`Analysis complete! Category: ${data.Kategorie || 'None'}, Username: ${data.Benutzername || 'None'}`);
            
        } else {
            button.innerHTML = 'Analysis Failed';
            emailCard.classList.remove('analyzing');
            showToast('Analysis failed: ' + data.message);
        }
    } catch (error) {
        console.error('Error analyzing email:', error);
        button.innerHTML = 'Analysis Failed';
        emailCard.classList.remove('analyzing');
        showToast('Analysis failed: Network error');
    }
    
    // Re-enable the button after a delay
    setTimeout(() => {
        button.innerHTML = 'Analyze Again';
    }, 2000);
}

// Handle execute action button click
async function handleExecuteAction(event) {
    const button = event.currentTarget;
    const emailId = parseInt(button.getAttribute('data-email-id'));
    
    // Find the email data
    const emailData = emails.find(email => email.id === emailId);
    if (!emailData || !emailData.analysisResult) {
        showToast('Email analysis data not found');
        return;
    }
    
    const category = emailData.analysisResult.Kategorie;
    const username = emailData.analysisResult.Benutzername;
    
    if (!category || !username) {
        showToast('Missing category or username for action');
        return;
    }
    
    // Show loading state
    button.disabled = true;
    button.innerHTML = `Executing <span class="loading"></span>`;
    
    try {
        // Call the execute action API
        const response = await fetch('/execute-action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category: category,
                username: username
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            button.textContent = 'Action Completed';
            showEditableToast(data.message);
            
            // Add a "completed" tag
            if (!emailData.tags.includes('Completed')) {
                emailData.tags.push('Completed');
                const tagsContainer = document.querySelector(`.email-card[data-email-id="${emailId}"] .email-tags`);
                tagsContainer.innerHTML = emailData.tags.map(tag => `<span class="tag ${tag === 'Completed' ? 'completed-tag' : ''}">${tag}</span>`).join('');
            }
        } else {
            button.textContent = 'Action Failed';
            showEditableToast('Action failed: ' + data.message);
        }
    } catch (error) {
        console.error('Error executing action:', error);
        button.textContent = 'Action Failed';
        showEditableToast('Action failed: Network error');
    }
    
    // Re-enable the button after a delay
    setTimeout(() => {
        button.disabled = false;
        button.textContent = `Execute: ${category}`;
    }, 3000);
}

// Show toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Show editable toast notification
function showEditableToast(message) {
    const toast = document.getElementById('toast');
    
    // Clear existing content
    toast.innerHTML = '';
    
    // Create editable field
    const editableContent = document.createElement('div');
    editableContent.contentEditable = true;
    editableContent.className = 'editable-content';
    editableContent.textContent = message;
    
    // Create close button
    const closeButton = document.createElement('button');
    closeButton.className = 'toast-close';
    closeButton.innerHTML = '&times;';
    closeButton.addEventListener('click', () => {
        toast.classList.remove('show');
    });
    
    // Add elements to toast
    toast.appendChild(editableContent);
    toast.appendChild(closeButton);
    
    // Show toast
    toast.classList.add('show');
    
    // Don't auto-hide editable toasts
}

// Search functionality
document.getElementById('search-input').addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    
    const filteredEmails = emails.filter(email => 
        email.subject.toLowerCase().includes(searchTerm) || 
        email.preview.toLowerCase().includes(searchTerm) || 
        email.sender.name.toLowerCase().includes(searchTerm) || 
        email.sender.email.toLowerCase().includes(searchTerm)
    );
    
    // Store the original emails
    const originalEmails = [...emails];
    
    // Replace with filtered emails temporarily
    emails = filteredEmails;
    currentPage = 1;
    renderEmails(currentPage);
    
    // Restore the original array if search is empty
    if (searchTerm.trim() === '') {
        emails = originalEmails;
        renderEmails(currentPage);
    }
});

// Initialize the email list on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchEmails();
    
    // Add refresh button functionality
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', fetchEmails);
    }
});