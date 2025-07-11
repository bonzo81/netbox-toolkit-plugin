/**
 * NetBox Toolkit Plugin - Consolidated JavaScript
 * 
 * This file contains all the JavaScript functionality for the NetBox Toolkit plugin
 * to avoid duplication across templates and improve maintainability.
 */

// Namespace for the toolkit functionality
window.NetBoxToolkit = window.NetBoxToolkit || {};

(function(Toolkit) {
    'use strict';
    
    // Prevent multiple initialization
    if (Toolkit.initialized) {
        console.log('NetBox Toolkit already initialized, skipping');
        return;
    }
    
    /**
     * Utility functions
     */
    Toolkit.Utils = {
        /**
         * Show success state on a button temporarily
         */
        showButtonSuccess: function(btn, successText = '<i class="mdi mdi-check me-1"></i>Copied!', duration = 2000) {
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
        fallbackCopyText: function(text, btn) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            
            try {
                textArea.focus();
                textArea.select();
                const successful = document.execCommand('copy');
                if (successful) {
                    this.showButtonSuccess(btn);
                } else {
                    console.error('Fallback copy command failed');
                    alert('Failed to copy to clipboard');
                }
            } catch (err) {
                console.error('Fallback copy failed:', err);
                alert('Failed to copy to clipboard');
            } finally {
                document.body.removeChild(textArea);
            }
        }
    };
    
    /**
     * Copy functionality for both parsed data and raw output
     * Works with multiple element ID patterns for flexibility
     */
    Toolkit.CopyManager = {
        /**
         * Initialize copy functionality for both parsed data and raw output buttons
         */
        init: function() {
            // Initialize parsed data copy buttons
            const copyParsedBtns = document.querySelectorAll('.copy-parsed-btn');
            copyParsedBtns.forEach(btn => {
                btn.addEventListener('click', this.handleCopyParsedData.bind(this));
            });
            
            // Initialize raw output copy buttons
            const copyOutputBtns = document.querySelectorAll('.copy-output-btn');
            copyOutputBtns.forEach(btn => {
                btn.addEventListener('click', this.handleCopyRawOutput.bind(this));
            });
        },
        
        /**
         * Handle copying raw command output from pre elements
         */
        handleCopyRawOutput: function(event) {
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
                    console.error('Failed to copy using Clipboard API:', err);
                    Toolkit.Utils.fallbackCopyText(outputText.trim(), btn);
                });
            } else {
                // Fallback for older browsers or non-secure contexts
                Toolkit.Utils.fallbackCopyText(outputText.trim(), btn);
            }
        },
        
        /**
         * Handle copying parsed data from JSON script elements
         */
        handleCopyParsedData: function(event) {
            const btn = event.target.closest('.copy-parsed-btn');
            if (!btn) return;
            
            // Try multiple possible element IDs for parsed data
            const possibleIds = [
                'parsed-data-json',           // device_toolkit.html
                'commandlog-parsed-data-json' // commandlog.html
            ];
            
            let parsedDataElement = null;
            for (const id of possibleIds) {
                parsedDataElement = document.getElementById(id);
                if (parsedDataElement) break;
            }
            
            if (!parsedDataElement) {
                console.error('No parsed data script element found with IDs:', possibleIds);
                alert('No parsed data found to copy');
                return;
            }
            
            const parsedDataStr = parsedDataElement.textContent;
            if (!parsedDataStr) {
                console.error('No parsed data found to copy');
                alert('No parsed data available');
                return;
            }
            
            try {
                // Parse and re-stringify for clean formatting
                const parsedData = JSON.parse(parsedDataStr);
                const formattedJson = JSON.stringify(parsedData, null, 2);
                
                // Use modern Clipboard API if available
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(formattedJson).then(() => {
                        Toolkit.Utils.showButtonSuccess(btn);
                    }).catch(err => {
                        console.error('Failed to copy using Clipboard API:', err);
                        Toolkit.Utils.fallbackCopyText(formattedJson, btn);
                    });
                } else {
                    // Fallback for older browsers or non-secure contexts
                    Toolkit.Utils.fallbackCopyText(formattedJson, btn);
                }
            } catch (err) {
                console.error('Error processing parsed data:', err);
                alert('Failed to process parsed data for copying: ' + err.message);
            }
        }
    };
    
    /**
     * Modal management for device toolkit
     */
    Toolkit.ModalManager = {
        instance: null,
        
        /**
         * Initialize modal functionality
         */
        init: function() {
            const credentialModal = document.getElementById('credentialModal');
            if (!credentialModal) return;
            
            // Try Bootstrap modal first, fallback to manual control
            try {
                if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                    this.instance = new bootstrap.Modal(credentialModal);
                    console.log('Bootstrap modal initialized successfully');
                } else {
                    console.log('Bootstrap not available, using manual modal control');
                    this.instance = this.createManualModal(credentialModal);
                }
            } catch (error) {
                console.error('Bootstrap modal initialization failed:', error);
                this.instance = this.createManualModal(credentialModal);
            }
            
            this.setupModalEvents(credentialModal);
        },
        
        /**
         * Create manual modal controls for fallback
         */
        createManualModal: function(modalElement) {
            return {
                show: function() {
                    modalElement.style.display = 'block';
                    modalElement.classList.add('show');
                    document.body.classList.add('modal-open');
                    
                    // Create backdrop
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-backdrop fade show';
                    backdrop.id = 'credentialModalBackdrop';
                    document.body.appendChild(backdrop);
                    
                    // Trigger shown event
                    const shownEvent = new Event('shown.bs.modal');
                    modalElement.dispatchEvent(shownEvent);
                },
                hide: function() {
                    modalElement.style.display = 'none';
                    modalElement.classList.remove('show');
                    document.body.classList.remove('modal-open');
                    
                    // Remove backdrop
                    const backdrop = document.getElementById('credentialModalBackdrop');
                    if (backdrop) {
                        backdrop.remove();
                    }
                    
                    // Trigger hidden event
                    const hiddenEvent = new Event('hidden.bs.modal');
                    modalElement.dispatchEvent(hiddenEvent);
                }
            };
        },
        
        /**
         * Setup modal event handlers
         */
        setupModalEvents: function(credentialModal) {
            // Handle close button clicks
            const modalCloseButton = credentialModal.querySelector('.btn-close');
            const modalCancelButton = credentialModal.querySelector('.btn-secondary');
            
            if (modalCloseButton) {
                modalCloseButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    if (this.instance) {
                        this.instance.hide();
                    }
                });
            }
            
            if (modalCancelButton) {
                modalCancelButton.addEventListener('click', (event) => {
                    event.preventDefault();
                    if (this.instance) {
                        this.instance.hide();
                    }
                });
            }
            
            // Handle backdrop clicks for manual modal
            credentialModal.addEventListener('click', (event) => {
                if (event.target === credentialModal && this.instance) {
                    this.instance.hide();
                }
            });
        },
        
        /**
         * Show the modal
         */
        show: function() {
            if (this.instance) {
                this.instance.show();
            }
        },
        
        /**
         * Hide the modal
         */
        hide: function() {
            if (this.instance) {
                this.instance.hide();
            }
        }
    };
    
    /**
     * Command execution functionality for device toolkit
     */
    Toolkit.CommandManager = {
        currentCommandData: null,
        
        /**
         * Initialize command execution functionality
         */
        init: function() {
            // Initialize modal first
            Toolkit.ModalManager.init();
            
            // Setup collapse toggle for connection info
            this.setupConnectionInfoToggle();
            
            // Setup command execution
            this.setupCommandExecution();
            
            // Setup modal form handlers
            this.setupModalForm();
        },
        
        /**
         * Setup connection info collapse toggle
         */
        setupConnectionInfoToggle: function() {
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
        },
        
        /**
         * Setup command execution event handlers
         */
        setupCommandExecution: function() {
            const commandContainer = document.querySelector('.card-commands');
            if (!commandContainer) {
                console.error('Command container not found');
                return;
            }
            
            // Use event delegation to avoid duplicate listeners
            commandContainer.removeEventListener('click', this.handleRunButtonClick.bind(this));
            commandContainer.addEventListener('click', this.handleRunButtonClick.bind(this));
        },
        
        /**
         * Handle run button clicks
         */
        handleRunButtonClick: function(event) {
            // Only handle clicks on run buttons
            const runButton = event.target.closest('.command-run-btn');
            if (!runButton) return;
            
            // Prevent any other event handlers from running
            event.preventDefault();
            event.stopImmediatePropagation();
            
            console.log('Run button clicked:', runButton);
            
            // Prevent double-clicks by checking if already processing
            if (runButton.dataset.processing === 'true') {
                console.log('Command already processing, ignoring click');
                return;
            }
            
            // Get the command item and set active state
            const commandItem = runButton.closest('.command-item');
            const allCommandItems = document.querySelectorAll('.command-item');
            allCommandItems.forEach(ci => ci.classList.remove('active'));
            commandItem.classList.add('active');
            
            // Store command data for modal
            const commandId = runButton.getAttribute('data-command-id');
            const commandName = runButton.getAttribute('data-command-name');
            
            this.currentCommandData = {
                id: commandId,
                name: commandName,
                element: commandItem,
                button: runButton,
                originalIconClass: runButton.querySelector('i').className
            };
            
            // Update modal content
            const commandToExecuteElement = document.getElementById('commandToExecute');
            if (commandToExecuteElement) {
                commandToExecuteElement.textContent = commandName;
            }
            
            // Clear previous credentials and show modal
            const modalUsernameField = document.getElementById('modalUsername');
            const modalPasswordField = document.getElementById('modalPassword');
            if (modalUsernameField) modalUsernameField.value = '';
            if (modalPasswordField) modalPasswordField.value = '';
            
            // Show the modal
            Toolkit.ModalManager.show();
            
            // Focus on username field when modal is shown
            const credentialModal = document.getElementById('credentialModal');
            if (credentialModal && modalUsernameField) {
                credentialModal.addEventListener('shown.bs.modal', function () {
                    modalUsernameField.focus();
                }, { once: true });
            }
        },
        
        /**
         * Setup modal form handlers
         */
        setupModalForm: function() {
            const executeCommandBtn = document.getElementById('executeCommandBtn');
            const modalUsernameField = document.getElementById('modalUsername');
            const modalPasswordField = document.getElementById('modalPassword');
            const credentialModal = document.getElementById('credentialModal');
            
            if (!executeCommandBtn) return;
            
            // Handle execute button click in modal
            executeCommandBtn.addEventListener('click', this.executeCommand.bind(this));
            
            // Handle Enter key in modal form
            if (modalPasswordField) {
                modalPasswordField.addEventListener('keypress', (event) => {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        executeCommandBtn.click();
                    }
                });
            }
            
            if (modalUsernameField) {
                modalUsernameField.addEventListener('keypress', (event) => {
                    if (event.key === 'Enter') {
                        event.preventDefault();
                        if (modalPasswordField) {
                            modalPasswordField.focus();
                        }
                    }
                });
            }
            
            // Clean up when modal is hidden
            if (credentialModal) {
                credentialModal.addEventListener('hidden.bs.modal', () => {
                    if (this.currentCommandData && this.currentCommandData.button.dataset.processing !== 'true') {
                        this.currentCommandData.element.classList.remove('active');
                    }
                    this.currentCommandData = null;
                    if (modalUsernameField) modalUsernameField.value = '';
                    if (modalPasswordField) modalPasswordField.value = '';
                });
            }
        },
        
        /**
         * Execute the selected command
         */
        executeCommand: function() {
            const modalUsernameField = document.getElementById('modalUsername');
            const modalPasswordField = document.getElementById('modalPassword');
            
            // Validate credentials
            if (!modalUsernameField?.value || !modalPasswordField?.value) {
                alert('Please enter both username and password');
                return;
            }
            
            if (!this.currentCommandData) {
                alert('No command selected');
                return;
            }
            
            console.log('Executing command:', this.currentCommandData);
            
            // Set processing flag and update UI
            this.setCommandProcessing(true);
            
            // Update output area
            this.showCommandRunning();
            
            // Prepare and submit form
            this.submitCommandForm();
        },
        
        /**
         * Set command processing state
         */
        setCommandProcessing: function(processing) {
            if (!this.currentCommandData) return;
            
            const button = this.currentCommandData.button;
            const buttonIcon = button.querySelector('i');
            
            button.dataset.processing = processing.toString();
            button.disabled = processing;
            
            if (processing) {
                buttonIcon.className = 'mdi mdi-loading mdi-spin';
            } else {
                buttonIcon.className = this.currentCommandData.originalIconClass;
            }
        },
        
        /**
         * Show command running state in output area
         */
        showCommandRunning: function() {
            const outputContainer = document.getElementById('commandOutputContainer');
            const commandHeader = document.querySelector('.output-card .card-header span.text-muted');
            
            if (outputContainer) {
                outputContainer.innerHTML = `
                    <div class="alert alert-primary d-flex align-items-center mb-0">
                        <div class="spinner-border spinner-border-sm me-3" role="status" aria-hidden="true" style="width: 1rem; height: 1rem; border-width: 0.125em;"></div>
                        <div>
                            <strong>Running command:</strong> ${this.currentCommandData.name}<br>
                            <small class="text-muted">Please wait while the command executes...</small>
                        </div>
                    </div>
                `;
            }
            
            // Update command header to show executing command
            if (commandHeader) {
                commandHeader.textContent = `Executing: ${this.currentCommandData.name}`;
            }
        },
        
        /**
         * Submit the command execution form
         */
        submitCommandForm: function() {
            const commandForm = document.getElementById('commandExecutionForm');
            const selectedCommandIdField = document.getElementById('selectedCommandId');
            const formUsernameField = document.getElementById('formUsername');
            const formPasswordField = document.getElementById('formPassword');
            const modalUsernameField = document.getElementById('modalUsername');
            const modalPasswordField = document.getElementById('modalPassword');
            
            if (!commandForm) {
                console.error('Command form not found');
                this.handleSubmissionError('Form not found');
                return;
            }
            
            // Prepare form data
            if (selectedCommandIdField) selectedCommandIdField.value = this.currentCommandData.id;
            if (formUsernameField) formUsernameField.value = modalUsernameField.value;
            if (formPasswordField) formPasswordField.value = modalPasswordField.value;
            
            console.log('Form data:', {
                commandId: selectedCommandIdField?.value,
                username: formUsernameField?.value,
                hasPassword: !!formPasswordField?.value
            });
            
            // Close modal
            Toolkit.ModalManager.hide();
            
            try {
                commandForm.submit();
            } catch (error) {
                console.error('Error submitting form:', error);
                this.handleSubmissionError('Error submitting form. Please check the console for details.');
            }
        },
        
        /**
         * Handle form submission errors
         */
        handleSubmissionError: function(message) {
            alert(message);
            
            // Reset processing state
            this.setCommandProcessing(false);
            
            // Show error in output container
            const outputContainer = document.getElementById('commandOutputContainer');
            const commandHeader = document.querySelector('.output-card .card-header span.text-muted');
            
            if (outputContainer) {
                outputContainer.innerHTML = `
                    <div class="alert alert-danger d-flex align-items-start mb-3">
                        <i class="mdi mdi-alert-circle me-2 mt-1"></i>
                        <div>
                            <strong>Form submission error</strong>
                            <br><small class="text-muted">${message}</small>
                        </div>
                    </div>
                    <div class="alert alert-info" id="defaultMessage">
                        Select a command to execute from the list on the left.
                    </div>
                `;
            }
            
            // Clear command header
            if (commandHeader) {
                commandHeader.textContent = '';
            }
        }
    };
    
    /**
     * Main initialization function
     */
    Toolkit.init = function() {
        console.log('Initializing NetBox Toolkit JavaScript');
        
        // Initialize copy functionality (available on all pages)
        this.CopyManager.init();
        
        // Initialize command functionality only if elements exist (device toolkit page)
        const commandForm = document.getElementById('commandExecutionForm');
        if (commandForm) {
            this.CommandManager.init();
        }
        
        this.initialized = true;
        console.log('NetBox Toolkit JavaScript initialized successfully');
    };
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            Toolkit.init();
        });
    } else {
        // DOM is already ready
        Toolkit.init();
    }
    
})(window.NetBoxToolkit);
