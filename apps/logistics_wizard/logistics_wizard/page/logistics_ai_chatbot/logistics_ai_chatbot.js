// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * Logistics AI Copilot - Conversational Interface Controller
 * Designed inspired by ChatGPT, Claude, and Gemini conversational UI standards.
 * Features:
 * - Collapsible multi-session conversation sidebar with search & grouping
 * - Interactive model & prompt configuration
 * - Markdown rendering with syntax-highlighted code blocks & instant copy
 * - Thinking/Reasoning accordion blocks (Claude 3.7 / DeepSeek style)
 * - Tool Call Execution cards (Function Calling visualization)
 * - Plug-and-play Developer Hook Bridge (window.LogisticsChatbotBridge)
 * - Strict Purple Ban compliance (Hex hues, RGB, HSL, Named colors)
 */

frappe.pages['logistics-ai-chatbot'] = frappe.pages['logistics-ai-chatbot'] || {};

frappe.pages['logistics-ai-chatbot'].on_page_load = function (wrapper) {
    wrapper.logisticsChatbotUI = new LogisticsAIChatbotUI(wrapper);
};

frappe.pages['logistics-ai-chatbot'].on_page_show = function (wrapper) {
    if (wrapper.logisticsChatbotUI) {
        wrapper.logisticsChatbotUI.focus_input();
    }
};

// Global Developer Hook Bridge for easy external AI and Tool plugging
window.LogisticsChatbotBridge = window.LogisticsChatbotBridge || {
    onSendMessage: null, // Override this function in custom scripts to intercept/stream AI logic
    registeredTools: {}
};

class LogisticsAIChatbotUI {
    constructor(wrapper) {
        this.wrapper = wrapper;
        this.sessionsKey = 'logistics_ai_chat_sessions_v2';
        this.settingsKey = 'logistics_ai_settings_v2';
        this.sessions = [];
        this.activeSessionId = null;
        this.isGenerating = false;
        this.attachedFiles = [];
        this.settings = this.load_settings();

        this.init_page();
        this.bind_events();
        this.load_sessions();
        this.apply_settings_to_ui();
    }

    init_page() {
        if (this.wrapper && typeof frappe !== 'undefined' && frappe.ui && frappe.ui.make_app_page) {
            this.page = frappe.ui.make_app_page({
                parent: this.wrapper,
                title: __('Logistics AI Copilot'),
                single_column: true
            });
            if (this.page && this.page.container) {
                this.page.container.removeClass('container').addClass('container-fluid');
                this.page.container.css({ 'max-width': '100%', 'padding': '0', 'margin': '0' });
            }
            const $w = $(this.wrapper);
            $w.closest('.page-container').addClass('logistics-full-width').css({ 'max-width': '100%', 'padding': '0', 'margin': '0' });
            $w.find('.page-content.container').removeClass('container').addClass('container-fluid');
            $w.find('.page-body, .page-content, .layout-main-section-wrapper, .layout-main-section').css({ 'max-width': '100%', 'padding': '0', 'margin': '0', 'border': 'none', 'box-shadow': 'none' });
            this.$body = $(this.page.body);
        } else {
            this.$body = $(this.wrapper || document.body);
        }

        // Render HTML template if not already mounted
        let renderedHtml = '';
        if (typeof frappe !== 'undefined' && frappe.templates && frappe.templates['logistics_ai_chatbot']) {
            renderedHtml = frappe.render_template('logistics_ai_chatbot', {});
        }
        if (renderedHtml && !this.$body.find('#logistics-ai-chat-app').length) {
            this.$body.html(renderedHtml);
        }

        this.$app = this.$body.find('#logistics-ai-chat-app');
        this.$sidebar = this.$app.find('#chat-sidebar');
        this.$messagesContainer = this.$app.find('#chat-messages-container');
        this.$welcomeScreen = this.$app.find('#chat-welcome-screen');
        this.$scrollContainer = this.$app.find('#chat-scroll-container');
        this.$textarea = this.$app.find('#chat-textarea');
        this.$btnSend = this.$app.find('#btn-send-message');
        this.$btnStop = this.$app.find('#btn-stop-generation');
        this.$attachmentsTray = this.$app.find('#chat-attachments-tray');
        this.$fileInput = this.$app.find('#file-input-hidden');
        this.$modelSelector = this.$app.find('#chat-model-selector');
        this.$settingsModal = this.$app.find('#chat-settings-modal');
        this.$searchInput = this.$app.find('#chat-search-input');
        this.$statusText = this.$app.find('#system-status-text');
    }

    load_settings() {
        const defaults = {
            apiEndpoint: '',
            modelName: 'gemini-2.5-flash',
            temperature: 0.2,
            apiKey: '',
            systemPrompt: 'Bạn là chuyên gia cố vấn Logistics và Quản trị Chi phí Landed Cost xuất nhập khẩu quốc tế.'
        };
        try {
            const raw = localStorage.getItem(this.settingsKey);
            return raw ? Object.assign({}, defaults, JSON.parse(raw)) : defaults;
        } catch (e) {
            return defaults;
        }
    }

    save_settings(settings) {
        this.settings = Object.assign({}, this.settings, settings);
        try {
            localStorage.setItem(this.settingsKey, JSON.stringify(this.settings));
        } catch (e) {
            console.error('Cannot save settings to localStorage', e);
        }
        this.apply_settings_to_ui();
    }

    apply_settings_to_ui() {
        if (!this.$app) return;
        this.$app.find('#cfg-api-endpoint').val(this.settings.apiEndpoint || '');
        this.$app.find('#cfg-model-name').val(this.settings.modelName || 'gemini-2.5-flash');
        this.$app.find('#cfg-temperature').val(this.settings.temperature || 0.2);
        this.$app.find('#cfg-api-key').val(this.settings.apiKey || '');
        this.$app.find('#cfg-system-prompt').val(this.settings.systemPrompt || '');

        if (this.settings.modelName) {
            this.$modelSelector.val(this.settings.modelName);
        }
        if (this.settings.apiEndpoint) {
            this.$statusText.text(__('Đã kết nối Backend API'));
        } else {
            this.$statusText.text(__('Developer Hook Sẵn sàng'));
        }
    }

    load_sessions() {
        try {
            const raw = localStorage.getItem(this.sessionsKey);
            this.sessions = raw ? JSON.parse(raw) : [];
        } catch (e) {
            this.sessions = [];
        }

        if (this.sessions.length === 0) {
            this.create_new_session(false);
        } else {
            this.switch_session(this.sessions[0].id);
        }
        this.render_sidebar_history();
    }

    save_sessions() {
        try {
            localStorage.setItem(this.sessionsKey, JSON.stringify(this.sessions));
        } catch (e) {
            console.error('Cannot save sessions to localStorage', e);
        }
        this.render_sidebar_history();
    }

    create_new_session(switchToIt = true) {
        const newSession = {
            id: 'session_' + Date.now(),
            title: __('Cuộc trò chuyện mới'),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            model: this.$modelSelector.val() || 'gemini-2.5-flash',
            messages: []
        };
        this.sessions.unshift(newSession);
        this.save_sessions();

        if (switchToIt) {
            this.switch_session(newSession.id);
        }
        return newSession;
    }

    switch_session(sessionId) {
        this.activeSessionId = sessionId;
        const session = this.get_active_session();
        if (!session) return;

        this.render_messages(session.messages);
        this.render_sidebar_history();
        this.focus_input();
    }

    get_active_session() {
        return this.sessions.find(s => s.id === this.activeSessionId) || null;
    }

    delete_session(sessionId, e) {
        if (e) e.stopPropagation();
        this.sessions = this.sessions.filter(s => s.id !== sessionId);
        if (this.sessions.length === 0) {
            this.create_new_session(true);
        } else if (this.activeSessionId === sessionId) {
            this.switch_session(this.sessions[0].id);
        } else {
            this.save_sessions();
        }
    }

    render_sidebar_history() {
        const query = (this.$searchInput.val() || '').toLowerCase().trim();
        const groups = {
            today: this.$app.find('#history-group-today .history-items-wrapper'),
            yesterday: this.$app.find('#history-group-yesterday .history-items-wrapper'),
            previous: this.$app.find('#history-group-previous .history-items-wrapper')
        };

        Object.values(groups).forEach($el => $el.empty());

        const now = new Date();
        const todayStr = now.toDateString();
        const yesterday = new Date(now);
        yesterday.setDate(yesterday.getDate() - 1);
        const yesterdayStr = yesterday.toDateString();

        let visibleCount = 0;

        this.sessions.forEach(session => {
            if (query && !session.title.toLowerCase().includes(query)) {
                return;
            }
            visibleCount++;

            const d = new Date(session.createdAt || Date.now());
            let targetGroup = groups.previous;
            if (d.toDateString() === todayStr) {
                targetGroup = groups.today;
            } else if (d.toDateString() === yesterdayStr) {
                targetGroup = groups.yesterday;
            }

            const isActive = session.id === this.activeSessionId;
            const $item = $(`
                <div class="history-item ${isActive ? 'active' : ''}" data-id="${session.id}">
                    <span class="history-item-title" title="${frappe.utils.escape_html(session.title)}">
                        ${frappe.utils.escape_html(session.title)}
                    </span>
                    <div class="history-item-actions">
                        <button class="btn-item-action btn-delete-chat" title="${__('Xóa')}">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                        </button>
                    </div>
                </div>
            `);

            $item.on('click', () => {
                this.switch_session(session.id);
            });

            $item.find('.btn-delete-chat').on('click', (ev) => {
                this.delete_session(session.id, ev);
            });

            targetGroup.append($item);
        });

        // Hide empty groups
        Object.entries(groups).forEach(([name, $el]) => {
            const $parent = $el.closest('.history-group');
            if ($el.children().length === 0) {
                $parent.hide();
            } else {
                $parent.show();
            }
        });
    }

    render_messages(messages) {
        this.$messagesContainer.empty();

        if (!messages || messages.length === 0) {
            this.$welcomeScreen.show();
            return;
        }

        this.$welcomeScreen.hide();
        messages.forEach(msg => {
            this.append_message_to_dom(msg);
        });
        this.scroll_to_bottom();
    }

    append_message_to_dom(msg) {
        this.$welcomeScreen.hide();

        const isUser = msg.role === 'user';
        const $row = $(`<div class="chat-message-row ${isUser ? 'user-row' : 'assistant-row'}"></div>`);

        if (isUser) {
            let attachmentsHtml = '';
            if (msg.attachments && msg.attachments.length > 0) {
                attachmentsHtml = `<div class="message-attachments-display">` +
                    msg.attachments.map(att => `
                        <span class="msg-attachment-chip">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                            </svg>
                            ${frappe.utils.escape_html(att.name)}
                        </span>
                    `).join('') + `</div>`;
            }

            const formattedContent = frappe.utils.escape_html(msg.content).replace(/\n/g, '<br>');
            $row.html(`
                <div class="user-bubble">
                    ${attachmentsHtml}
                    <div>${formattedContent}</div>
                </div>
            `);
        } else {
            // Assistant message
            let thinkingHtml = '';
            if (msg.thinking) {
                thinkingHtml = `
                    <div class="thinking-accordion">
                        <div class="thinking-header">
                            <div class="thinking-header-left">
                                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <path d="M12 16v-4"></path>
                                    <path d="M12 8h.01"></path>
                                </svg>
                                <span>Quá trình suy luận & phân tích chuyên sâu</span>
                            </div>
                            <svg class="thinking-header-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </div>
                        <div class="thinking-content">${frappe.utils.escape_html(msg.thinking)}</div>
                    </div>
                `;
            }

            let toolCallsHtml = '';
            if (msg.toolCalls && msg.toolCalls.length > 0) {
                toolCallsHtml = msg.toolCalls.map(tc => `
                    <div class="tool-call-card">
                        <div class="tool-card-header">
                            <div class="tool-card-left">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                                </svg>
                                <span>Công cụ: <code>${frappe.utils.escape_html(tc.name)}</code></span>
                            </div>
                            <span class="tool-badge ${tc.running ? 'running' : ''}">${tc.running ? 'Đang gọi...' : 'Hoàn tất'}</span>
                        </div>
                        <div class="tool-card-body">
                            <pre><code>${frappe.utils.escape_html(JSON.stringify(tc.result || tc.args || {}, null, 2))}</code></pre>
                        </div>
                    </div>
                `).join('');
            }

            const markdownParsed = this.parse_markdown(msg.content);

            $row.html(`
                <div class="assistant-avatar">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                    </svg>
                </div>
                <div class="assistant-bubble">
                    ${thinkingHtml}
                    ${toolCallsHtml}
                    <div class="message-markdown">${markdownParsed}</div>
                </div>
            `);

            // Bind accordion toggle
            $row.find('.thinking-header').on('click', function () {
                $(this).closest('.thinking-accordion').toggleClass('open');
            });

            // Bind code copy buttons
            $row.find('.btn-copy-code').on('click', function () {
                const codeText = $(this).closest('.code-block-container').find('code').text();
                navigator.clipboard.writeText(codeText).then(() => {
                    const $btn = $(this);
                    $btn.html('✓ Đã sao chép');
                    setTimeout(() => {
                        $btn.html(`
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                            <span>Sao chép</span>
                        `);
                    }, 2000);
                });
            });
        }

        this.$messagesContainer.append($row);
        return $row;
    }

    parse_markdown(text) {
        if (!text) return '';

        // 1. Process fenced code blocks
        const codeBlocks = [];
        let processed = text.replace(/```([a-zA-Z0-9_\-\.\s]*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const index = codeBlocks.length;
            const language = lang.trim() || 'code';
            const escapedCode = frappe.utils.escape_html(code.trim());
            const blockHtml = `
                <div class="code-block-container">
                    <div class="code-block-header">
                        <span>${frappe.utils.escape_html(language.toUpperCase())}</span>
                        <button class="btn-copy-code">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                            </svg>
                            <span>Sao chép</span>
                        </button>
                    </div>
                    <pre><code class="language-${frappe.utils.escape_html(language)}">${escapedCode}</code></pre>
                </div>
            `;
            codeBlocks.push(blockHtml);
            return `__CODE_BLOCK_${index}__`;
        });

        // 2. Process Markdown Tables
        processed = processed.replace(/((?:\|[^\n]+\|\n?){2,})/g, (match) => {
            const lines = match.trim().split('\n');
            if (lines.length < 2) return match;

            const parseRow = (line) => line.split('|').slice(1, -1).map(c => c.trim());
            const headers = parseRow(lines[0]);
            const isSeparator = (line) => /^\|(\s*:?-+:?\s*\|)+$/.test(line.trim());

            let startIndex = 1;
            if (isSeparator(lines[1])) {
                startIndex = 2;
            }

            let tableHtml = '<table class="markdown-table"><thead><tr>';
            headers.forEach(h => {
                tableHtml += `<th>${frappe.utils.escape_html(h)}</th>`;
            });
            tableHtml += '</tr></thead><tbody>';

            for (let i = startIndex; i < lines.length; i++) {
                if (isSeparator(lines[i])) continue;
                const cells = parseRow(lines[i]);
                tableHtml += '<tr>';
                cells.forEach(c => {
                    tableHtml += `<td>${frappe.utils.escape_html(c)}</td>`;
                });
                tableHtml += '</tr>';
            }
            tableHtml += '</tbody></table>';
            return tableHtml;
        });

        // 3. Headers
        processed = processed.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        processed = processed.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        processed = processed.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // 4. Blockquotes
        processed = processed.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

        // 5. Bold & Italic
        processed = processed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        processed = processed.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // 6. Inline Code
        processed = processed.replace(/`([^`]+)`/g, (m, c) => `<code>${frappe.utils.escape_html(c)}</code>`);

        // 7. Unordered Lists
        processed = processed.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
        processed = processed.replace(/(<li>.*<\/li>)/gis, '<ul>$1</ul>');

        // 8. Paragraphs and Line Breaks
        const paragraphs = processed.split(/\n{2,}/);
        processed = paragraphs.map(p => {
            if (p.startsWith('<h') || p.startsWith('<blockquote') || p.startsWith('<table') || p.startsWith('<ul>') || p.startsWith('__CODE_BLOCK_')) {
                return p;
            }
            return `<p>${p.replace(/\n/g, '<br>')}</p>`;
        }).join('');

        // Re-inject Code Blocks
        codeBlocks.forEach((block, idx) => {
            processed = processed.replace(`__CODE_BLOCK_${idx}__`, block);
        });

        return processed;
    }

    scroll_to_bottom() {
        if (!this.$scrollContainer) return;
        this.$scrollContainer.stop().animate({
            scrollTop: this.$scrollContainer[0].scrollHeight
        }, 150);
    }

    focus_input() {
        if (this.$textarea) {
            this.$textarea.focus();
        }
    }

    bind_events() {
        const self = this;

        // Auto-resize textarea
        this.$textarea.on('input', function () {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
            const val = $(this).val().trim();
            self.$btnSend.prop('disabled', val.length === 0 && self.attachedFiles.length === 0);
        });

        // Enter key to send (Shift+Enter for newline)
        this.$textarea.on('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                self.handle_send_action();
            }
        });

        // Send button click
        this.$btnSend.on('click', () => {
            this.handle_send_action();
        });

        // Stop generation button
        this.$btnStop.on('click', () => {
            this.stop_generation();
        });

        // New chat button
        this.$app.find('#btn-new-chat').on('click', () => {
            this.create_new_session(true);
        });

        // Sidebar toggle button
        this.$app.find('#btn-toggle-sidebar').on('click', () => {
            this.$sidebar.toggleClass('collapsed');
        });

        // Quick prompts click
        this.$app.find('.quick-prompt-card').on('click', function () {
            const promptText = $(this).data('prompt');
            if (promptText) {
                self.$textarea.val(promptText);
                self.$textarea.trigger('input');
                self.handle_send_action();
            }
        });

        // Search in history
        this.$searchInput.on('input', () => {
            this.render_sidebar_history();
        });

        // Attachment file button
        this.$app.find('#btn-attach-file').on('click', () => {
            this.$fileInput.trigger('click');
        });

        this.$fileInput.on('change', function () {
            const files = Array.from(this.files || []);
            files.forEach(f => {
                self.attachedFiles.push({
                    name: f.name,
                    size: f.size,
                    type: f.type
                });
            });
            $(this).val('');
            self.render_attachments_tray();
            self.$textarea.trigger('input');
        });

        // Model selector change
        this.$modelSelector.on('change', function () {
            const selected = $(this).val();
            const session = self.get_active_session();
            if (session) {
                session.model = selected;
                self.save_sessions();
            }
        });

        // Clear chat
        this.$app.find('#btn-clear-chat').on('click', () => {
            frappe.confirm(__('Bạn có chắc muốn xóa toàn bộ tin nhắn trong cuộc trò chuyện này?'), () => {
                const session = self.get_active_session();
                if (session) {
                    session.messages = [];
                    session.title = __('Cuộc trò chuyện mới');
                    self.save_sessions();
                    self.render_messages([]);
                }
            });
        });

        // Export chat
        this.$app.find('#btn-export-chat').on('click', () => {
            this.export_current_chat();
        });

        // Settings Modal Open/Close
        this.$app.find('#btn-open-settings, #btn-header-settings').on('click', () => {
            this.$settingsModal.fadeIn(150);
        });

        this.$app.find('#btn-close-settings-modal, #btn-cancel-settings').on('click', () => {
            this.$settingsModal.fadeOut(150);
        });

        // Settings Tabs
        this.$app.find('.settings-tab-btn').on('click', function () {
            const tabId = $(this).data('tab');
            self.$app.find('.settings-tab-btn').removeClass('active');
            $(this).addClass('active');
            self.$app.find('.settings-tab-content').removeClass('active');
            self.$app.find('#' + tabId).addClass('active');
        });

        // Save Settings
        this.$app.find('#btn-save-settings').on('click', () => {
            const newSettings = {
                apiEndpoint: this.$app.find('#cfg-api-endpoint').val().trim(),
                modelName: this.$app.find('#cfg-model-name').val().trim(),
                temperature: parseFloat(this.$app.find('#cfg-temperature').val()) || 0.2,
                apiKey: this.$app.find('#cfg-api-key').val().trim(),
                systemPrompt: this.$app.find('#cfg-system-prompt').val().trim()
            };
            this.save_settings(newSettings);
            this.$settingsModal.fadeOut(150);
            frappe.show_alert({
                message: __('Đã lưu cấu hình AI & Backend Tools thành công!'),
                indicator: 'green'
            });
        });
    }

    render_attachments_tray() {
        this.$attachmentsTray.empty();
        if (this.attachedFiles.length === 0) {
            this.$attachmentsTray.hide();
            return;
        }

        this.$attachmentsTray.show();
        this.attachedFiles.forEach((file, idx) => {
            const $pill = $(`
                <span class="attachment-pill">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                    </svg>
                    <span>${frappe.utils.escape_html(file.name)}</span>
                    <button class="btn-remove-attachment" data-idx="${idx}">&times;</button>
                </span>
            `);

            $pill.find('.btn-remove-attachment').on('click', () => {
                this.attachedFiles.splice(idx, 1);
                this.render_attachments_tray();
                this.$textarea.trigger('input');
            });

            this.$attachmentsTray.append($pill);
        });
    }

    handle_send_action() {
        const text = this.$textarea.val().trim();
        const files = [...this.attachedFiles];

        if (!text && files.length === 0) return;
        if (this.isGenerating) return;

        const session = this.get_active_session();
        if (!session) return;

        // Reset inputs
        this.$textarea.val('').css('height', 'auto');
        this.attachedFiles = [];
        this.render_attachments_tray();
        this.$btnSend.prop('disabled', true);

        // Update session title on first message
        if (session.messages.length === 0) {
            session.title = text.slice(0, 42) + (text.length > 42 ? '...' : '');
        }

        // 1. Append User Message
        const userMsg = {
            role: 'user',
            content: text,
            attachments: files,
            timestamp: new Date().toISOString()
        };
        session.messages.push(userMsg);
        session.updatedAt = new Date().toISOString();
        this.save_sessions();
        this.append_message_to_dom(userMsg);
        this.scroll_to_bottom();

        // 2. Prepare Assistant Message Placeholder
        this.isGenerating = true;
        this.$btnSend.hide();
        this.$btnStop.show();

        const assistantMsg = {
            role: 'assistant',
            content: '',
            thinking: '',
            toolCalls: [],
            timestamp: new Date().toISOString()
        };
        session.messages.push(assistantMsg);

        const $assistantRow = this.append_message_to_dom(assistantMsg);
        const $markdownArea = $assistantRow.find('.message-markdown');
        $markdownArea.html(`
            <div class="typing-dots">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        `);
        this.scroll_to_bottom();

        // 3. Dispatch to Developer Bridge or Default AI Handler
        this.dispatch_to_ai_bridge(text, session, assistantMsg, $assistantRow);
    }

    dispatch_to_ai_bridge(userPrompt, session, assistantMsg, $assistantRow) {
        const self = this;
        let streamedText = '';

        const callbacks = {
            onThinking: (thinkingText) => {
                if (!self.isGenerating) return;
                assistantMsg.thinking = (assistantMsg.thinking || '') + thinkingText;
                let $thinking = $assistantRow.find('.thinking-accordion');
                if (!$thinking.length) {
                    $assistantRow.find('.assistant-bubble').prepend(`
                        <div class="thinking-accordion open">
                            <div class="thinking-header">
                                <div class="thinking-header-left">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                        <circle cx="12" cy="12" r="10"></circle>
                                        <path d="M12 16v-4"></path>
                                        <path d="M12 8h.01"></path>
                                    </svg>
                                    <span>Quá trình suy luận & phân tích chuyên sâu</span>
                                </div>
                                <svg class="thinking-header-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polyline points="6 9 12 15 18 9"></polyline>
                                </svg>
                            </div>
                            <div class="thinking-content"></div>
                        </div>
                    `);
                    $thinking = $assistantRow.find('.thinking-accordion');
                    $thinking.find('.thinking-header').on('click', function () {
                        $(this).closest('.thinking-accordion').toggleClass('open');
                    });
                }
                $thinking.find('.thinking-content').text(assistantMsg.thinking);
                self.scroll_to_bottom();
            },

            onToolCall: (toolName, toolArgs, toolResult) => {
                if (!self.isGenerating) return;
                const tc = {
                    name: toolName,
                    args: toolArgs,
                    result: toolResult,
                    running: false
                };
                assistantMsg.toolCalls.push(tc);

                const toolHtml = `
                    <div class="tool-call-card">
                        <div class="tool-card-header">
                            <div class="tool-card-left">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                                </svg>
                                <span>Công cụ: <code>${frappe.utils.escape_html(toolName)}</code></span>
                            </div>
                            <span class="tool-badge">Hoàn tất</span>
                        </div>
                        <div class="tool-card-body">
                            <pre><code>${frappe.utils.escape_html(JSON.stringify(toolResult || toolArgs || {}, null, 2))}</code></pre>
                        </div>
                    </div>
                `;
                $assistantRow.find('.message-markdown').before(toolHtml);
                self.scroll_to_bottom();
            },

            onStreamChunk: (chunk) => {
                if (!self.isGenerating) return;
                streamedText += chunk;
                assistantMsg.content = streamedText;
                $assistantRow.find('.message-markdown').html(self.parse_markdown(streamedText));
                self.scroll_to_bottom();
            },

            onComplete: (finalText) => {
                if (!self.isGenerating) return;
                assistantMsg.content = finalText || streamedText;
                $assistantRow.find('.message-markdown').html(self.parse_markdown(assistantMsg.content));
                self.finish_generation(session);
            },

            onError: (err) => {
                const errMsg = typeof err === 'string' ? err : (err.message || 'Lỗi không xác định khi kết nối AI');
                $assistantRow.find('.message-markdown').html(`
                    <div style="color: #ef4444; background: #fee2e2; padding: 10px 14px; border-radius: 8px; border: 1px solid #fca5a5;">
                        <strong>⚠️ Lỗi xử lý:</strong> ${frappe.utils.escape_html(errMsg)}
                    </div>
                `);
                self.finish_generation(session);
            }
        };

        // 1. Check if user configured Developer Hook in window.LogisticsChatbotBridge
        if (typeof window.LogisticsChatbotBridge.onSendMessage === 'function') {
            try {
                window.LogisticsChatbotBridge.onSendMessage(
                    userPrompt,
                    session.messages.slice(0, -1),
                    { settings: self.settings, session_id: session.id },
                    callbacks
                );
            } catch (err) {
                callbacks.onError(err);
            }
            return;
        }

        // 2. Check if user configured a Custom API Endpoint in Settings Modal
        if (this.settings.apiEndpoint) {
            this.call_custom_api_endpoint(userPrompt, session, callbacks);
            return;
        }

        // 3. Default Built-in Mock / Demonstration Engine with Real Logistics Domain Intelligence
        this.execute_default_demonstration(userPrompt, session, callbacks);
    }

    call_custom_api_endpoint(userPrompt, session, callbacks) {
        callbacks.onThinking(__('Đang kết nối tới API Endpoint: ') + this.settings.apiEndpoint);

        const historyPayload = session.messages.slice(0, -1).map(m => ({
            role: m.role,
            content: m.content
        }));

        const bodyData = {
            model: this.settings.modelName || 'gemini-2.5-flash',
            messages: [
                { role: 'system', content: this.settings.systemPrompt || '' },
                ...historyPayload
            ],
            temperature: this.settings.temperature || 0.2
        };

        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.settings.apiKey) {
            headers['Authorization'] = 'Bearer ' + this.settings.apiKey;
        }

        fetch(this.settings.apiEndpoint, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(bodyData)
        })
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            return res.json();
        })
        .then(data => {
            let reply = '';
            if (data.choices && data.choices[0] && data.choices[0].message) {
                reply = data.choices[0].message.content;
            } else if (data.message) {
                reply = typeof data.message === 'string' ? data.message : JSON.stringify(data.message);
            } else {
                reply = JSON.stringify(data, null, 2);
            }
            callbacks.onComplete(reply);
        })
        .catch(err => {
            callbacks.onError(err);
        });
    }

    execute_default_demonstration(userPrompt, session, callbacks) {
        const lower = userPrompt.toLowerCase();
        const self = this;

        setTimeout(() => {
            callbacks.onThinking("Đang phân tích ngữ cảnh nghiệp vụ Logistics, cấu trúc Trade Case và tra cứu dữ liệu liên quan...\n- Nhận diện thực thể: Hồ sơ nhập khẩu / giá vốn Landed Cost\n- Tải các luật phân bổ chi phí (Allocation Engine) và chỉ số phương sai (Variance)");
        }, 300);

        setTimeout(() => {
            // SCENARIO 1: Costing / Landed Cost
            if (lower.includes('cost') || lower.includes('giá vốn') || lower.includes('chi phí') || lower.includes('variance') || lower.includes('lô hàng')) {
                callbacks.onToolCall('get_case_cost_summary', { case_id: 'IMP-2026-001' }, {
                    case_id: 'IMP-2026-001',
                    purchase_value: 125000.0,
                    estimated_cost: 16800.0,
                    actual_cost: 18350.0,
                    variance_amount: 1550.0,
                    variance_pct: 9.23,
                    actual_landed_cost: 143350.0,
                    invoices_received: 6,
                    invoices_total: 6,
                    costs_allocated: 18350.0,
                    cost_finalization_status: 'Fully Allocated'
                });

                const streamResponse = [
                    "Dựa trên hồ sơ ngoại thương **IMP-2026-001** (Lô hàng Thép cuộn cán nóng nhập khẩu từ Cảng Thượng Hải về Cảng Tiên Sa, Đà Nẵng):\n\n",
                    "### 📊 Tổng Hợp Chi Phí Landed Cost & Phương Sai (Variance)\n\n",
                    "| Chỉ số | Dự toán (Estimated) | Thực tế (Actual) | Chênh lệch (Variance) | Đánh giá |\n",
                    "| :--- | :--- | :--- | :--- | :--- |\n",
                    "| **Trị giá hàng (FOB)** | $125,000.00 | $125,000.00 | $0.00 (0.0%) | Khớp 100% |\n",
                    "| **Cước biển quốc tế (Ocean Freight)** | $7,500.00 | $8,200.00 | +$700.00 (+9.3%) | Phụ phí Bunker |\n",
                    "| **Bảo hiểm hàng hải (Insurance)** | $600.00 | $600.00 | $0.00 (0.0%) | Chuẩn theo HĐ |\n",
                    "| **Thuế NK & VAT (Duty & Tax)** | $5,200.00 | $5,450.00 | +$250.00 (+4.8%) | Tỷ giá hải quan |\n",
                    "| **Phí cảng & Nâng hạ (Port & Handling)** | $1,800.00 | $2,100.00 | +$300.00 (+16.7%) | Lưu kho bãi (Demurrage) |\n",
                    "| **Vận chuyển nội địa (Trucking)** | $1,700.00 | $2,000.00 | +$300.00 (+17.6%) | Phụ phí giờ cao điểm |\n",
                    "| **TỔNG CHI PHÍ LOGISTICS** | **$16,800.00** | **$18,350.00** | **+$1,550.00 (+9.23%)** | Vượt dự toán 9.23% |\n\n",
                    "### 💡 Phân bổ Giá Vốn Thực Tế (Cost Allocation by Weight)\n",
                    "- Toàn bộ **$18,350.00** chi phí thực tế đã được đồng bộ sang phiếu **Landed Cost Voucher (LCV-2026-0004)**.\n",
                    "- Giá vốn đơn vị sau phân bổ: **$573.40 / Tấn** (tăng $6.20/tấn so với giá dự kiến ban đầu).\n",
                    "- **Khuyến nghị**: Đối chiếu lại hóa đơn lưu kho bãi với hãng tàu Maersk để xác nhận tính hợp lệ của khoản phụ thu demurrage $300."
                ];

                let idx = 0;
                const timer = setInterval(() => {
                    if (!self.isGenerating) {
                        clearInterval(timer);
                        return;
                    }
                    if (idx < streamResponse.length) {
                        callbacks.onStreamChunk(streamResponse[idx]);
                        idx++;
                    } else {
                        clearInterval(timer);
                        callbacks.onComplete();
                    }
                }, 100);

            // SCENARIO 2: Vessel & Tracking
            } else if (lower.includes('tàu') || lower.includes('vessel') || lower.includes('tracking') || lower.includes('đà nẵng') || lower.includes('gps')) {
                callbacks.onToolCall('track_vessel_telemetry', { vessel_name: 'MAERSK MC-KINNEY MOLLER' }, {
                    mmsi: '219018271',
                    latitude: 16.1284,
                    longitude: 108.2391,
                    speed_knots: 14.8,
                    heading: 215,
                    destination: 'VN DAD (TIEN SA PORT)',
                    eta: '2026-10-18 14:00:00 ICT',
                    status: 'Underway Using Engine'
                });

                const streamResponse = [
                    "### 🚢 Giám sát Hải trình Tàu & Vận đơn Hải quan\n\n",
                    "- **Tàu chuyên tuyến**: `MAERSK MC-KINNEY MOLLER` (MMSI: 219018271)\n",
                    "- **Vị trí hiện tại**: Tọa độ `16.1284° N, 108.2391° E` (Vịnh Đà Nẵng, cách phao số 0 khoảng 4.2 hải lý).\n",
                    "- **Tốc độ di chuyển**: 14.8 knots | Hướng di chuyển: 215° Nam-Tây Nam.\n",
                    "- **Dự kiến cập cảng (ETA)**: **14:00 ngày 18/10/2026** tại Cầu cảng số 3, Cảng Tiên Sa.\n\n",
                    "> **Lưu ý nghiệp vụ**: Vui lòng hoàn tất truyền tờ khai hải quan điện tử qua hệ thống VNACCS trước 10:00 sáng mai để kịp thời nhận phân luồng Vàng/Xanh khi hoa tiêu dẫn tàu cập bến."
                ];

                let idx = 0;
                const timer = setInterval(() => {
                    if (!self.isGenerating) {
                        clearInterval(timer);
                        return;
                    }
                    if (idx < streamResponse.length) {
                        callbacks.onStreamChunk(streamResponse[idx]);
                        idx++;
                    } else {
                        clearInterval(timer);
                        callbacks.onComplete();
                    }
                }, 120);

            // SCENARIO 3: General Logistics Consultation
            } else {
                const streamResponse = [
                    "Chào bạn! Tôi đã ghi nhận yêu cầu của bạn về: **" + userPrompt + "**.\n\n",
                    "Giao diện **Logistics AI Copilot** đã được chuẩn bị đầy đủ các cổng tích hợp:\n",
                    "1. **Cấu hình mô hình AI**: Bạn có thể vào biểu tượng ⚙️ (Cấu hình) ở góc trên bên phải để nhập API Endpoint (OpenAI, Gemini, Ollama, Frappe API).\n",
                    "2. **Developer Hook (window.LogisticsChatbotBridge)**: Bạn có thể viết logic backend hoặc function calling tùy ý để trả về dữ liệu thời gian thực.\n",
                    "3. **Tương thích toàn diện**: Hỗ trợ đầy đủ bảng biểu, mã nguồn, khối suy luận (Thinking) và thẻ thực thi Tool.\n\n",
                    "Bạn cần tôi hỗ trợ kiểm tra thêm phần nghiệp vụ nào trong phân hệ Ngoại thương & Chi phí Landed Cost?"
                ];

                let idx = 0;
                const timer = setInterval(() => {
                    if (!self.isGenerating) {
                        clearInterval(timer);
                        return;
                    }
                    if (idx < streamResponse.length) {
                        callbacks.onStreamChunk(streamResponse[idx]);
                        idx++;
                    } else {
                        clearInterval(timer);
                        callbacks.onComplete();
                    }
                }, 100);
            }
        }, 800);
    }

    stop_generation() {
        this.isGenerating = false;
        const session = this.get_active_session();
        this.finish_generation(session);
    }

    finish_generation(session) {
        this.isGenerating = false;
        this.$btnStop.hide();
        this.$btnSend.show();
        this.$textarea.trigger('input');
        if (session) {
            this.save_sessions();
        }
        this.focus_input();
    }

    export_current_chat() {
        const session = this.get_active_session();
        if (!session || !session.messages || session.messages.length === 0) {
            frappe.msgprint(__('Cuộc trò chuyện hiện chưa có tin nhắn nào để xuất.'));
            return;
        }

        let markdownContent = `# ${session.title}\n`;
        markdownContent += `*Thời gian: ${new Date(session.createdAt).toLocaleString('vi-VN')} | Model: ${session.model}*\n\n---\n\n`;

        session.messages.forEach(m => {
            const roleName = m.role === 'user' ? '👤 Người dùng' : '🤖 Trợ lý AI Logistics';
            markdownContent += `### ${roleName} (${new Date(m.timestamp).toLocaleTimeString('vi-VN')}):\n\n`;
            if (m.thinking) {
                markdownContent += `> **Suy luận:**\n> ${m.thinking.replace(/\n/g, '\n> ')}\n\n`;
            }
            markdownContent += `${m.content}\n\n---\n\n`;
        });

        const blob = new Blob([markdownContent], { type: 'text/markdown;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `logistics-chat-${session.id}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

if (typeof window !== 'undefined') {
    window.LogisticsAIChatbotUI = LogisticsAIChatbotUI;
}
