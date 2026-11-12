// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * Global Logistics AI Copilot - Floating Action Widget (FAB) & Popup Drawer
 * Automatically mounts on all Desk pages via app_include_js
 */

(function () {
    'use strict';

    if (typeof window === 'undefined') return;

    function initLogisticsAIWidget() {
        // Prevent mounting multiple times
        if ($('#logistics-ai-fab-container').length) return;

        // Skip if unauthenticated
        if (typeof frappe !== 'undefined' && frappe.session && frappe.session.user === 'Guest') {
            return;
        }

        const widgetHtml = `
            <!-- FLOATING ACTION BUTTON (FAB) -->
            <div id="logistics-ai-fab-container">
                <span class="fab-tooltip-pill">Trợ lý Logistics AI</span>
                <button id="btn-logistics-fab" class="logistics-fab-btn" title="Mở Trợ lý AI Logistics">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span class="fab-badge-dot"></span>
                </button>
            </div>

            <!-- POPUP CHAT DRAWER -->
            <div id="logistics-ai-drawer" style="display: none;">
                <div class="drawer-header">
                    <div class="drawer-header-brand">
                        <div class="drawer-avatar">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                            </svg>
                        </div>
                        <div class="drawer-header-info">
                            <span class="drawer-title">Logistics Copilot</span>
                            <span class="drawer-sub">● Trực tuyến & Sẵn sàng</span>
                        </div>
                    </div>
                    <div class="drawer-header-actions">
                        <button id="btn-drawer-rag-admin" class="drawer-action-btn" title="Kho tri thức RAG">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
                                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
                                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
                            </svg>
                        </button>
                        <button id="btn-drawer-fullscreen" class="drawer-action-btn" title="Mở trang đầy đủ">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="15 3 21 3 21 9"></polyline>
                                <polyline points="9 21 3 21 3 15"></polyline>
                                <line x1="21" y1="3" x2="14" y2="10"></line>
                                <line x1="3" y1="21" x2="10" y2="14"></line>
                            </svg>
                        </button>
                        <button id="btn-drawer-close" class="drawer-action-btn" title="Thu nhỏ về chấm tròn">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                </div>

                <div id="drawer-messages-body" class="drawer-body">
                    <div id="drawer-welcome-state" class="drawer-welcome-box">
                        <div class="drawer-welcome-icon">🚢</div>
                        <div class="drawer-welcome-text">
                            <strong>Xin chào!</strong> Tôi là Trợ lý AI chuyên trách về Biểu thuế XNK, Thông tư 85, Landed Cost và hành trình tàu.
                        </div>
                        <div class="drawer-quick-prompts">
                            <button class="drawer-prompt-btn" data-q="Theo Thông tư 85/2026/TT-BTC, máy móc thiết bị tháo rời được phân loại theo quy tắc nào?">
                                📜 Thông tư 85 & Máy móc tháo rời
                            </button>
                            <button class="drawer-prompt-btn" data-q="Phân tích chi tiết sai lệch chi phí thực tế so với dự toán hồ sơ IMP-2026-001">
                                📊 Phân tích sai lệch chi phí IMP-2026-001
                            </button>
                            <button class="drawer-prompt-btn" data-q="Cho biết vị trí tọa độ AIS và ngày cập cảng của tàu Maersk Mc-Kinney Moller">
                                🚢 Theo dõi tàu Maersk về Đà Nẵng
                            </button>
                            <button class="drawer-prompt-btn btn-open-rag-admin-center" style="border-left: 3px solid #0284c7; background: #f0f9ff; font-weight: 600; color: #0369a1; text-align: left;">
                                ⚙️ Quản trị RAG & Kho Tri Thức HS &rarr;
                            </button>
                        </div>
                    </div>
                </div>

                <div class="drawer-footer">
                    <div class="drawer-input-row">
                        <textarea id="drawer-textarea" class="drawer-textarea" placeholder="Hỏi nhanh AI Logistics... (Enter gửi)" rows="1"></textarea>
                        <button id="btn-drawer-send" class="drawer-btn-send" disabled title="Gửi câu hỏi">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <line x1="12" y1="19" x2="12" y2="5"></line>
                                <polyline points="5 12 12 5 19 12"></polyline>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        $('body').append(widgetHtml);
        bindWidgetEvents();
    }

    function bindWidgetEvents() {
        const $fab = $('#btn-logistics-fab');
        const $drawer = $('#logistics-ai-drawer');
        const $textarea = $('#drawer-textarea');
        const $btnSend = $('#btn-drawer-send');
        const $messagesBody = $('#drawer-messages-body');
        const $welcome = $('#drawer-welcome-state');

        // Toggle Drawer
        $fab.on('click', function (e) {
            e.stopPropagation();
            if ($drawer.is(':visible')) {
                $drawer.fadeOut(150);
            } else {
                $drawer.fadeIn(180);
                $textarea.focus();
            }
        });

        // Close Drawer (shrink back to small circle)
        $('#btn-drawer-close').on('click', function () {
            $drawer.fadeOut(150);
        });

        // Navigate to RAG Admin Center
        $(document).on('click', '#btn-drawer-rag-admin, .btn-open-rag-admin-center', function (e) {
            e.preventDefault();
            $drawer.fadeOut(150);
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.set_route('rag-knowledge-base');
            } else {
                window.location.href = '/app/rag-knowledge-base';
            }
        });

        // Fullscreen action -> Navigate to Logistics AI Copilot Page
        $('#btn-drawer-fullscreen').on('click', function () {
            $drawer.fadeOut(150);
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.set_route('logistics-ai-copilot');
            } else {
                window.location.href = '/app/logistics-ai-copilot';
            }
        });

        // Auto-expand textarea
        $textarea.on('input', function () {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            $btnSend.prop('disabled', $(this).val().trim().length === 0);
        });

        // Enter key to send
        $textarea.on('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Send click
        $btnSend.on('click', function () {
            sendMessage();
        });

        // Quick prompts
        $('.drawer-prompt-btn').on('click', function () {
            const prompt = $(this).data('q');
            if (prompt) {
                $textarea.val(prompt);
                $textarea.trigger('input');
                sendMessage();
            }
        });

        function sendMessage() {
            const text = $textarea.val().trim();
            if (!text) return;

            $welcome.hide();
            $textarea.val('').css('height', 'auto');
            $btnSend.prop('disabled', true);

            // 1. Append User Msg
            appendMessage('user', text);

            // 2. Append Assistant Placeholder
            const $assistantRow = appendMessage('assistant', '<span class="typing-dots"><i class="fa fa-circle-o-notch fa-spin"></i> Đang suy luận...</span>');

            // 3. Call backend API
            if (typeof frappe !== 'undefined' && frappe.call) {
                frappe.call({
                    method: 'logistics_wizard.api.ask_ai_copilot',
                    args: {
                        query: text,
                        case_id: 'IMP-2026-001',
                        drawer: true
                    },
                    callback: function (r) {
                        if (r && r.message && r.message.success) {
                            const data = r.message;
                            let html = '';
                            if (data.thinking) {
                                const stepOne = data.thinking.split('\n')[0] || 'Truy xuất RAG';
                                html += `<div class="drawer-thinking-mini">💡 <em>${frappe.utils.escape_html(stepOne)}</em></div>`;
                            }
                            html += `<div class="drawer-answer-content">${data.answer || ''}</div>`;
                            if (Array.isArray(data.sources) && data.sources.length) {
                                html += `<div class="drawer-sources-mini"><strong>Nguồn:</strong> ${data.sources.map(s => frappe.utils.escape_html(s.title)).join(', ')}</div>`;
                            }
                            $assistantRow.find('.drawer-msg-bubble').html(html);
                        } else {
                            const err = (r && r.message && r.message.error) || 'Lỗi xử lý câu hỏi';
                            $assistantRow.find('.drawer-msg-bubble').html(`<span style="color:#ef4444;"><i class="fa fa-exclamation-triangle"></i> Lỗi: ${frappe.utils.escape_html(err)}</span>`);
                        }
                        scrollToBottom();
                    },
                    error: function () {
                        $assistantRow.find('.drawer-msg-bubble').html(`<span style="color:#ef4444;"><i class="fa fa-exclamation-triangle"></i> Lỗi kết nối API</span>`);
                        scrollToBottom();
                    }
                });
            } else {
                setTimeout(() => {
                    $assistantRow.find('.drawer-msg-bubble').html('Hệ thống AI Copilot đang trực tuyến.');
                    scrollToBottom();
                }, 400);
            }
        }

        function appendMessage(role, htmlContent) {
            const isUser = role === 'user';
            const escaped = isUser ? frappe.utils.escape_html(htmlContent).replace(/\n/g, '<br>') : htmlContent;
            const $row = $(`
                <div class="drawer-msg-row ${role}">
                    <div class="drawer-msg-bubble">
                        ${escaped}
                    </div>
                </div>
            `);
            $messagesBody.append($row);
            scrollToBottom();
            return $row;
        }

        function scrollToBottom() {
            $messagesBody.stop().animate({ scrollTop: $messagesBody[0].scrollHeight }, 100);
        }
    }

    // Mount on boot
    if (typeof frappe !== 'undefined' && frappe.ready) {
        frappe.ready(initLogisticsAIWidget);
    } else {
        $(document).ready(initLogisticsAIWidget);
    }

    // Export to window
    if (typeof window !== 'undefined') {
        window.initLogisticsAIWidget = initLogisticsAIWidget;
    }
})();
