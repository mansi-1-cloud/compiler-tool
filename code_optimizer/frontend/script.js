/**
 * Code Optimizer Frontend
 * Handles UI interactions, API calls, and code optimization visualization
 */

// Configuration
const API_BASE_URL = 'http://localhost:5001';
const DEBOUNCE_DELAY = 300;

// DOM Elements
const originalCodeEl = document.getElementById('original-code');
const optimizedCodeEl = document.getElementById('optimized-code');
const optimizeBtn = document.getElementById('optimize-btn');
const loadSampleBtn = document.getElementById('load-sample-btn');
const clearBtn = document.getElementById('clear-btn');
const copyBtn = document.getElementById('copy-btn');
const languageSelect = document.getElementById('language-select');
const statusMessage = document.getElementById('status-message');
const loadingSpinner = document.getElementById('loading-spinner');
const detailsPanel = document.getElementById('details-panel');
const closeDetailsBtn = document.getElementById('close-details');
const optimizationsList = document.getElementById('optimizations-list');

// Statistics elements
const statTotal = document.getElementById('stat-total');
const statOriginal = document.getElementById('stat-original');
const statOptimized = document.getElementById('stat-optimized');
const statSaved = document.getElementById('stat-saved');
const originalLineCount = document.getElementById('original-line-count');
const optimizedLineCount = document.getElementById('optimized-line-count');
const optimizationCategories = document.getElementById('optimization-categories');

// State
let currentLanguage = 'java';
let lastOptimizationResult = null;

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    optimizeBtn.addEventListener('click', optimizeCode);
    loadSampleBtn.addEventListener('click', loadSampleCode);
    clearBtn.addEventListener('click', clearAllCode);
    copyBtn.addEventListener('click', copyOptimizedCode);
    languageSelect.addEventListener('change', (e) => {
        currentLanguage = e.target.value;
        lineCountCheck();
    });
    
    if (closeDetailsBtn) {
        closeDetailsBtn.addEventListener('click', () => {
            detailsPanel.style.display = 'none';
        });
    }

    // Update line counts as user types
    originalCodeEl.addEventListener('input', debounce(lineCountCheck, 200));
    optimizedCodeEl.addEventListener('input', debounce(lineCountCheck, 200));
}

/**
 * Debounce function for performance
 */
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

/**
 * Update line counts display
 */
function lineCountCheck() {
    const originalLines = originalCodeEl.value.split('\n').length;
    const optimizedLines = optimizedCodeEl.value.split('\n').length;

    originalLineCount.textContent = `Lines: ${originalLines}`;
    optimizedLineCount.textContent = `Lines: ${optimizedLines}`;
}

/**
 * Show status message
 */
function showStatus(message, type = 'info', duration = 4000) {
    statusMessage.textContent = message;
    statusMessage.className = `status-message show ${type}`;

    if (duration > 0) {
        setTimeout(() => {
            statusMessage.classList.remove('show');
        }, duration);
    }
}

/**
 * Show loading spinner
 */
function showLoading(show = true) {
    loadingSpinner.style.display = show ? 'flex' : 'none';
}

/**
 * Get file extension based on language
 */
function getFileExtension(language) {
    const extensions = {
        'java': '.java',
        'cpp': '.cpp',
        'c': '.c',
        'c++': '.cpp'
    };
    return extensions[language] || '';
}

/**
 * Optimize code via API
 */
async function optimizeCode() {
    const code = originalCodeEl.value.trim();

    if (!code) {
        showStatus('Please enter some code to optimize', 'info');
        return;
    }

    showLoading(true);
    optimizeBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/optimize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                language: currentLanguage,
                extension: getFileExtension(currentLanguage)
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Optimization failed');
        }

        const result = await response.json();

        if (result.success) {
            // Update UI with results
            optimizedCodeEl.value = result.optimized_code;
            lastOptimizationResult = result;

            // Update statistics
            updateStatistics(result.statistics);

            // Update optimization categories
            updateOptimizationCategories(result.statistics.optimization_categories);

            // Show optimizations with line numbers
            displayOptimizationDetails(result.optimizations_applied);

            showStatus(
                `✨ Code optimized successfully! ${result.statistics.total_optimizations} optimizations applied.`, 
                'success',
                5000
            );
            copyBtn.style.display = result.optimized_code ? 'block' : 'none';
            lineCountCheck();
        } else {
            throw new Error(result.error || 'Unknown error occurred');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
        console.error('Optimization error:', error);
    } finally {
        showLoading(false);
        optimizeBtn.disabled = false;
    }
}

/**
 * Update statistics display
 */
function updateStatistics(stats) {
    statTotal.textContent = stats.total_optimizations || 0;
    statOriginal.textContent = stats.original_lines || 0;
    statOptimized.textContent = stats.optimized_lines || 0;
    statSaved.textContent = stats.lines_saved || 0;
}

/**
 * Update optimization categories display
 */
function updateOptimizationCategories(categories) {
    optimizationCategories.innerHTML = '';

    if (Object.keys(categories).length === 0) {
        optimizationCategories.innerHTML = '<p style="color: var(--text-light); font-size: 0.85rem;">No optimizations found</p>';
        return;
    }

    const categoryNames = {
        'constant_folding': '🔢 Constant Folding',
        'dead_code_elimination': '🗑️ Dead Code Elimination',
        'unused_variable_removal': '🔍 Unused Variables',
        'redundant_assignment_removal': '♻️ Redundant Assignments',
        'loop_elimination': '🔁 Loop Elimination',
        'function_inlining': '📦 Function Inlining',
        'duplicate_call_removal': '🔄 Duplicate Calls',
        'variable_combination': '🔗 Variable Combination'
    };

    for (const [category, count] of Object.entries(categories)) {
        const categoryItem = document.createElement('div');
        categoryItem.className = 'category-item';
        categoryItem.innerHTML = `
            <span class="category-name">${categoryNames[category] || category}</span>
            <span class="category-count">${count}</span>
        `;
        optimizationCategories.appendChild(categoryItem);
    }
}

/**
 * Display detailed optimization information WITH LINE NUMBERS
 */
function displayOptimizationDetails(optimizations) {
    if (!optimizations || optimizations.length === 0) {
        detailsPanel.style.display = 'none';
        return;
    }

    optimizationsList.innerHTML = '';

    optimizations.forEach((opt) => {
        const optItem = document.createElement('div');
        optItem.className = `optimization-item optimization-${opt.type}`;

        // Create header with line number and type
        const header = document.createElement('div');
        header.className = 'optimization-header';
        header.innerHTML = `
            <span class="line-number">[Line ${opt.line_number}]</span>
            <span class="optimization-type">${formatOptimizationType(opt.type)}</span>
        `;

        // Create details section
        const details = document.createElement('div');
        details.className = 'optimization-details';

        // Format details based on optimization type
        let detailsContent = '';

        if (opt.type === 'constant_folding') {
            detailsContent = `
                <p><strong>Expression:</strong> <code>${escapeHtml(opt.optimization)}</code></p>
            `;
        } else if (opt.type === 'unused_variable_removal') {
            detailsContent = `
                <p><strong>Variable:</strong> ${escapeHtml(opt.optimization)}</p>
            `;
        } else if (opt.type === 'dead_code_elimination') {
            detailsContent = `
                <p><strong>Removed:</strong> <code>${escapeHtml(opt.optimization)}</code></p>
            `;
        } else if (opt.type === 'redundant_assignment_removal') {
            detailsContent = `
                <p><strong>Variable:</strong> ${escapeHtml(opt.optimization)}</p>
            `;
        } else if (opt.type === 'loop_elimination') {
            detailsContent = `
                <p><strong>Optimization:</strong> <code>${escapeHtml(opt.optimization)}</code></p>
            `;
        } else if (opt.type === 'function_inlining') {
            detailsContent = `
                <p><strong>Optimization:</strong> ${escapeHtml(opt.optimization)}</p>
            `;
        } else if (opt.type === 'duplicate_call_removal') {
            detailsContent = `
                <p><strong>Optimization:</strong> ${escapeHtml(opt.optimization)}</p>
            `;
        } else if (opt.type === 'variable_combination') {
            detailsContent = `
                <p><strong>Optimization:</strong> ${escapeHtml(opt.optimization)}</p>
            `;
        } else {
            detailsContent = `
                <p><strong>Optimization:</strong> ${escapeHtml(opt.optimization)}</p>
            `;
        }

        details.innerHTML = detailsContent;

        optItem.appendChild(header);
        optItem.appendChild(details);
        optimizationsList.appendChild(optItem);
    });

    detailsPanel.style.display = 'block';
}

/**
 * Format optimization type name
 */
function formatOptimizationType(type) {
    const names = {
        'constant_folding': 'Constant Folding',
        'dead_code_elimination': 'Dead Code Elimination',
        'unused_variable_removal': 'Unused Variable Removal',
        'redundant_assignment_removal': 'Redundant Assignment Removal',
        'loop_elimination': 'Loop Elimination',
        'function_inlining': 'Function Inlining',
        'duplicate_call_removal': 'Duplicate Call Removal',
        'variable_combination': 'Variable Combination'
    };
    
    return names[type] || type
        .split('_')
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Load sample code for selected language
 */
async function loadSampleCode() {
    try {
        const response = await fetch(`${API_BASE_URL}/sample-code?language=${currentLanguage}`);

        if (!response.ok) {
            throw new Error('Failed to load sample code');
        }

        const result = await response.json();
        originalCodeEl.value = result.sample_code.trim();
        optimizedCodeEl.value = '';
        lineCountCheck();
        resetStatistics();

        showStatus('Sample code loaded. Click "Optimize Code" to see optimizations!', 'info', 4000);
    } catch (error) {
        showStatus(`Error loading sample: ${error.message}`, 'error');
        console.error('Error:', error);
    }
}

/**
 * Clear all code and reset UI
 */
function clearAllCode() {
    originalCodeEl.value = '';
    optimizedCodeEl.value = '';
    detailsPanel.style.display = 'none';
    copyBtn.style.display = 'none';
    resetStatistics();
    lineCountCheck();

    showStatus('Code cleared', 'info', 2000);
}

/**
 * Reset statistics display
 */
function resetStatistics() {
    statTotal.textContent = '0';
    statOriginal.textContent = '0';
    statOptimized.textContent = '0';
    statSaved.textContent = '0';
    optimizationCategories.innerHTML = '';
}

/**
 * Copy optimized code to clipboard
 */
async function copyOptimizedCode() {
    const code = optimizedCodeEl.value;

    if (!code) {
        showStatus('No optimized code to copy', 'info');
        return;
    }

    try {
        await navigator.clipboard.writeText(code);
        showStatus('✓ Optimized code copied to clipboard!', 'success', 2000);
    } catch (error) {
        showStatus('Failed to copy code', 'error');
        console.error('Copy error:', error);
    }
}

/**
 * Check backend health on page load
 */
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            throw new Error('Backend not responding');
        }
        const result = await response.json();
        console.log('Backend health:', result);
    } catch (error) {
        showStatus(
            '⚠️ Backend server not reachable. Make sure Flask server is running on port 5001.', 
            'error', 
            0
        );
        console.error('Health check failed:', error);
    }
}

/**
 * Initialize on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    checkBackendHealth();
    lineCountCheck();

    // Add keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to optimize
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && document.activeElement === originalCodeEl) {
            optimizeCode();
        }
    });
});

// Handle API errors gracefully
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    showStatus('An unexpected error occurred', 'error');
});