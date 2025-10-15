/**
 * NetBox Toolkit Plugin - Consolidated JavaScript
 *
 * This file contains all the JavaScript functionality for the NetBox Toolkit plugin
 * to avoid duplication across templates and improve maintainability.
 */

// Namespace for the toolkit functionality
window.NetBoxToolkit = window.NetBoxToolkit || {};

(function (Toolkit) {
    'use strict';

    // Prevent multiple initialization
    if (Toolkit.initialized) {
        return;
    }

    /**
     * Utility functions
     */
    Toolkit.Utils = {
        /**
         * Show success state on a button temporarily
         */
        showButtonSuccess: function (btn, successText = '<i class="mdi mdi-check me-1"></i>Copied!', duration = 2000) {
            const originalText = btn.innerHTML;
            const originalClass = btn.className;

            btn.classList.add('copied');
            btn.innerHTML = successText;
            btn.style.backgroundColor = 'var(--tblr-success)';
            btn.style.borderColor = 'var(--tblr-success)';
            btn.style.color = 'white';

            setTimeout(() => {
                btn.className = originalClass;
                btn.innerHTML = originalText;
                btn.style.backgroundColor = '';
                btn.style.borderColor = '';
                btn.style.color = '';
            }, duration);
        },

        /**
         * Fallback text copy using document.execCommand (legacy browsers)
         */
        fallbackCopyText: function (text, btn) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            textArea.style.opacity = '0';
            textArea.style.pointerEvents = 'none';
            textArea.style.tabIndex = '-1';

            if (!document.body.contains(textArea)) {
                document.body.appendChild(textArea);
            }

            try {
                // Only preserve selection if user has an active selection
                // This avoids expensive operations when unnecessary
                const selection = document.getSelection();
                const previousRange = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

                textArea.focus();
                textArea.select();
                textArea.setSelectionRange(0, text.length);

                const successful = document.execCommand('copy');

                if (successful) {
                    this.showButtonSuccess(btn);
                } else {
                    console.error('All clipboard copy methods failed');
                    alert('Failed to copy to clipboard. Please copy manually.');
                }
            } catch (err) {
                console.error('Fallback copy error:', err.message);
                alert('Failed to copy to clipboard. Please copy manually.');
            } finally {
                // Only restore selection if one existed
                if (previousRange) {
                    const selection = document.getSelection();
                    selection.removeAllRanges();
                    selection.addRange(previousRange);
                }

                if (document.body.contains(textArea)) {
                    document.body.removeChild(textArea);
                }
            }
        },

        /**
         * Copy text to clipboard (modern approach)
         */
        copyToClipboard: function (btn, text) {
            if (!text) {
                console.error('No text provided to copy');
                alert('No text available to copy');
                return;
            }

            // Use modern Clipboard API if available
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text.trim()).then(() => {
                    this.showButtonSuccess(btn);
                }).catch(err => {
                    console.warn('Clipboard API failed, using fallback:', err.message);
                    this.fallbackCopyText(text.trim(), btn);
                });
            } else {
                // Fallback for older browsers or non-secure contexts
                this.fallbackCopyText(text.trim(), btn);
            }
        }
    };

    /**
     * Copy functionality for parsed data and raw output
     * Works with multiple element ID patterns for flexibility
     * CSV downloads are handled by Django API endpoints
     */
    Toolkit.CopyManager = {
        // Track initialization state at module level
        _delegationInitialized: false,

        /**
         * Initialize copy functionality using event delegation
         * This prevents duplicate event listeners when content is swapped
         */
        init: function () {
            // Use event delegation instead of individual button listeners
            // This prevents duplicate listeners when HTMX swaps content
            if (!this._delegationInitialized) {
                document.body.addEventListener('click', this.handleDelegatedClick.bind(this));
                this._delegationInitialized = true;
            }
        },

        /**
         * Handle all click events through delegation
         */
        handleDelegatedClick: function (event) {
            const target = event.target.closest('button');
            if (!target) return;

            if (target.classList.contains('copy-parsed-btn')) {
                this.handleCopyParsedData(event);
            } else if (target.classList.contains('copy-output-btn')) {
                this.handleCopyRawOutput(event);
            } else if (target.classList.contains('copy-token-btn')) {
                this.handleCopyToken(event);
            }
        },

        /**
         * Clean up existing event listeners (called before re-initialization)
         */
        cleanup: function () {
            // Event delegation doesn't need cleanup since it's on body
        },

        /**
         * Handle copying raw command output from pre elements
         */
        handleCopyRawOutput: function (event) {
            const btn = event.target.closest('.copy-output-btn');
            if (!btn) return;

            // Find the command output element
            // Look for .command-output within the same tab pane or nearby
            const tabPane = btn.closest('.tab-pane') || btn.closest('.card-body') || document;
            const outputElement = tabPane.querySelector('.command-output');

            if (!outputElement) {
                console.error('No command output element found');
                alert('No command output found to copy');
                return;
            }

            const outputText = outputElement.textContent || outputElement.innerText;
            if (!outputText || !outputText.trim()) {
                console.error('No command output text found');
                alert('No command output available to copy');
                return;
            }

            // Use modern Clipboard API if available
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(outputText.trim()).then(() => {
                    Toolkit.Utils.showButtonSuccess(btn);
                }).catch(err => {
                    console.warn('Clipboard API failed, using fallback:', err.message);
                    Toolkit.Utils.fallbackCopyText(outputText.trim(), btn);
                });
            } else {
                // Fallback for older browsers or non-secure contexts
                Toolkit.Utils.fallbackCopyText(outputText.trim(), btn);
            }
        },

        /**
         * Handle copying parsed data from data attribute or script elements
         */
        handleCopyParsedData: function (event) {
            const btn = event.target.closest('.copy-parsed-btn');
            if (!btn) return;

            let parsedDataStr = null;

            // First try to get data from the button's data attribute
            if (btn.dataset.parsedData) {
                parsedDataStr = btn.dataset.parsedData;
            } else {
                // Fallback to script elements for backward compatibility
                const possibleIds = [
                    'parsed-data-json',           // device_toolkit.html
                    'commandlog-parsed-data-json' // commandlog.html
                ];

                for (const id of possibleIds) {
                    const element = document.getElementById(id);
                    if (element) {
                        parsedDataStr = element.textContent;
                        break;
                    }
                }
            }

            if (!parsedDataStr || parsedDataStr.trim() === '') {
                console.error('No parsed data found to copy');
                alert('No parsed data found to copy');
                return;
            }

            // Check if it's valid JSON before trying to parse
            let formattedJson = null;
            try {
                const parsedData = JSON.parse(parsedDataStr);
                formattedJson = JSON.stringify(parsedData, null, 2);
            } catch (parseErr) {
                // If it's not JSON, just copy the raw text
                formattedJson = parsedDataStr;
            }

            // Use modern Clipboard API if available
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(formattedJson).then(() => {
                    Toolkit.Utils.showButtonSuccess(btn);
                }).catch(err => {
                    console.warn('Clipboard API failed, using fallback:', err.message);
                    Toolkit.Utils.fallbackCopyText(formattedJson, btn);
                });
            } else {
                // Fallback for older browsers or non-secure contexts
                Toolkit.Utils.fallbackCopyText(formattedJson, btn);
            }
        },

        /**
         * Handle copying credential token from data attribute
         */
        handleCopyToken: function (event) {
            const btn = event.target.closest('.copy-token-btn');
            if (!btn) return;

            const token = btn.dataset.token;
            if (!token) {
                console.error('No token data attribute found');
                alert('No token available to copy');
                return;
            }

            Toolkit.Utils.copyToClipboard(btn, token);
        }
    };

    /**
     * Command execution functionality for device toolkit
     */
    Toolkit.CommandManager = {
        /**
         * Initialize command functionality
         */
        init: function () {
            // Setup collapse toggle for connection info
            this.setupConnectionInfoToggle();
        },

        /**
         * Setup connection info collapse toggle
         */
        setupConnectionInfoToggle: function () {
            const connectionInfoCollapse = document.getElementById('connectionInfoCollapse');
            const connectionInfoToggleButton = document.querySelector('[data-bs-target="#connectionInfoCollapse"]');

            if (connectionInfoCollapse && connectionInfoToggleButton) {
                connectionInfoCollapse.addEventListener('hidden.bs.collapse', function () {
                    connectionInfoToggleButton.classList.add('collapsed');
                });

                connectionInfoCollapse.addEventListener('shown.bs.collapse', function () {
                    connectionInfoToggleButton.classList.remove('collapsed');
                });
            }
        }
    };

    /**
     * Variable Formset Manager
     * Handles deletion of command variables and total form count management
     * Form addition is now handled by HTMX
     */
    Toolkit.VariableFormsetManager = {
        /**
         * Initialize variable formset functionality
         */
        init: function () {
            const variableFormsContainer = document.getElementById('variable-forms');
            const totalFormsInput = document.querySelector('#id_variables-TOTAL_FORMS');

            if (!variableFormsContainer || !totalFormsInput) {
                return; // Not on command edit page
            }

            // Handle delete buttons (using event delegation for dynamically added forms)
            variableFormsContainer.addEventListener('click', function (e) {
                if (e.target.closest('.delete-variable')) {
                    const formToDelete = e.target.closest('.variable-form');
                    if (formToDelete) {
                        formToDelete.remove();
                        this.updateFormIndices();
                    }
                }
            }.bind(this));
        },

        /**
         * Update form indices and total count after deletion
         */
        updateFormIndices: function () {
            const variableFormsContainer = document.getElementById('variable-forms');
            const totalFormsInput = document.querySelector('#id_variables-TOTAL_FORMS');

            if (!variableFormsContainer || !totalFormsInput) {
                return;
            }

            const forms = variableFormsContainer.querySelectorAll('.variable-form');

            // Update TOTAL_FORMS count
            totalFormsInput.value = forms.length;

            // Update form indices in names and IDs
            forms.forEach((form, index) => {
                form.setAttribute('data-form-index', index);

                // Update all input names and IDs
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    if (input.name && input.name.includes('variables-')) {
                        input.name = input.name.replace(/variables-\d+-/, `variables-${index}-`);
                    }
                    if (input.id && input.id.includes('variables-')) {
                        input.id = input.id.replace(/variables-\d+-/, `variables-${index}-`);
                    }
                });

                // Update label for attributes
                const labels = form.querySelectorAll('label');
                labels.forEach(label => {
                    if (label.getAttribute('for') && label.getAttribute('for').includes('variables-')) {
                        label.setAttribute('for',
                            label.getAttribute('for').replace(/variables-\d+-/, `variables-${index}-`)
                        );
                    }
                });
            });
        }
    };

    /**
     * HTMX Event Manager
     * Handles HTMX-specific events for modal management and content swapping
     */
    Toolkit.HTMXManager = {
        /**
         * Initialize HTMX event handlers
         */
        init: function () {
            // Only initialize if HTMX is available
            if (typeof htmx === 'undefined') {
                return;
            }

            // HTMX after swap event handler
            document.addEventListener('htmx:afterSwap', this.handleAfterSwap.bind(this));

            // HTMX after request event handler
            document.addEventListener('htmx:afterRequest', this.handleAfterRequest.bind(this));
        },

        /**
         * Handle HTMX afterSwap events
         */
        handleAfterSwap: function (evt) {
            if (evt.detail.target.id === 'htmx-modal-container') {
                // Modal was loaded, add backdrop click handler
                this.setupModalHandlers(evt.detail.target);
                // Reinitialize tooltips in the modal content
                window.NetBoxToolkit.TooltipManager.init();
            } else if (evt.detail.target.tagName === 'BODY') {
                // Body content was swapped (after command execution)
                // With event delegation, we don't need to re-initialize CopyManager
                // But we do need to reinitialize tooltips
                window.NetBoxToolkit.TooltipManager.init();
            } else {
                // Any other content swap (partial updates)
                // Reinitialize tooltips for the new content
                window.NetBoxToolkit.TooltipManager.init();
            }
        },

        /**
         * Handle HTMX afterRequest events
         */
        handleAfterRequest: function (evt) {
            if (evt.detail.xhr.status === 200 && evt.detail.target.tagName === 'FORM') {
                // Form submitted successfully, modal should be closed by body swap
            }
        },

        /**
         * Setup modal backdrop and escape key handlers
         */
        setupModalHandlers: function (container) {
            const modal = container.querySelector('.modal');
            const backdrop = container.querySelector('.modal-backdrop');
            const closeButtons = container.querySelectorAll('[data-modal-close]');

            if (modal && backdrop) {
                // Backdrop click handler
                backdrop.addEventListener('click', function () {
                    Toolkit.HTMXManager.closeModal();
                });

                // Escape key handler (one-time use)
                document.addEventListener('keydown', function (e) {
                    if (e.key === 'Escape') {
                        Toolkit.HTMXManager.closeModal();
                    }
                }, { once: true });
            }

            // All modal close button handlers (handles both btn-close and btn-secondary)
            closeButtons.forEach(function (button) {
                button.addEventListener('click', function (e) {
                    e.preventDefault();
                    Toolkit.HTMXManager.closeModal();
                });
            });
        },

        /**
         * Close the HTMX modal
         */
        closeModal: function () {
            const modalContainer = document.getElementById('htmx-modal-container');
            if (modalContainer) {
                modalContainer.innerHTML = '';
            }
        }
    };

    /**
     * Bootstrap Tooltip Manager
     */
    Toolkit.TooltipManager = {
        /**
         * Initialize Bootstrap tooltips
         */
        init: function () {
            // Initialize tooltips for elements with data-bs-toggle="tooltip"
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                // Dispose existing tooltips first to avoid duplicates
                const existingTooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
                existingTooltips.forEach(function (element) {
                    const existingTooltip = bootstrap.Tooltip.getInstance(element);
                    if (existingTooltip) {
                        existingTooltip.dispose();
                    }
                });

                // Initialize new tooltips
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
        }
    };

    /**
     * Main initialization function
     */
    Toolkit.init = function () {
        // Initialize copy functionality (available on all pages)
        this.CopyManager.init();

        // Initialize Bootstrap tooltips (available on all pages)
        this.TooltipManager.init();

        // Initialize HTMX functionality (device toolkit page)
        this.HTMXManager.init();

        // Initialize variable formset functionality (command edit page)
        this.VariableFormsetManager.init();

        // Initialize command functionality only if elements exist (device toolkit page)
        const commandForm = document.getElementById('commandExecutionForm');
        if (commandForm) {
            this.CommandManager.init();
        }

        this.initialized = true;
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            Toolkit.init();
        });
    } else {
        // DOM is already ready
        Toolkit.init();
    }

})(window.NetBoxToolkit);
