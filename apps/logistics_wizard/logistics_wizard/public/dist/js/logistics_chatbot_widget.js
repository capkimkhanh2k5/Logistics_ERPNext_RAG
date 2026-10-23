// Copyright (c) 2026, Logistics Wizard and contributors
// For license information, please see license.txt

/**
 * Global Logistics AI Copilot - Floating Action Widget & Drawer
 * Automatically mounts on all Desk pages via app_include_js
 */

(function () {
    'use strict';

    if (typeof window === 'undefined') return;

    function initLogisticsAIWidget() {
        // Prevent mounting multiple times
        if ($('#logistics-ai-fab-container').length) return;

        // Skip if inside login or unauthenticated view
        if (typeof frappe !== 'undefined' && frappe.session && frappe.session.user === 'Guest') {
            return;
        }

        const widgetHtml = `
            <!-- FLOATING ACTION BUTTON (FAB) -->
            <div id="logistics-ai-fab-container">
                <span class="fab-tooltip-pill">Logistics AI Copilot</span>
                <button id="btn-logistics-fab" class="logistics-fab-btn" title="Mở Trợ lý AI Logistics">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                    <span class="fab-badge-dot"></span>
                </button>
            </div>

            <!-- POPUP CHAT DRAWER -->
            <div id="logistics-ai-drawer">
                <div class="drawer-header">
                    <div class="drawer-header-brand">
                        <div class="drawer-avatar">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                            </svg>
                        </div>
                        <div class="drawer-header-info">
                            <span class="drawer-title">Logistics Copilot</span>
                            <span class="drawer-sub">● Trực tuyến & Sẵn sàng</span>
                        </div>
                    </div>
                    <div class="drawer-header-actions">
                        <button id="btn-drawer-fullscreen" class="drawer-action-btn" title="Mở trang đầy đủ">
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="15 3 21 3 21 9"></polyline>
                                <polyline points="9 21 3 21 3 15"></polyline>
                                <line x1="21" y1="3" x2="14" y2="10"></line>
                                <line x1="3" y1="21" x2="10" y2="14"></line>
                            </svg>
                        </button>
                        <button id="btn-drawer-close" class="drawer-action-btn" title="Thu nhỏ">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
                            Xin chào! Tôi có thể giải đáp nhanh thông tin Trade Case, giá vốn Landed Cost và hành trình tàu.
                        </div>
                        <div class="drawer-quick-prompts">
                            <button class="drawer-prompt-btn" data-q="Tra cứu hồ sơ Trade Case IMP-2026-001">
                                📦 Tra cứu hồ sơ IMP-2026-001
                            </button>
                            <button class="drawer-prompt-btn" data-q="Phân tích Landed Cost và phương sai chi phí thực tế">
                                📊 Phân tích Landed Cost & Variance
                            </button>
                            <button class="drawer-prompt-btn" data-q="Tọa độ và ngày cập cảng của tàu MAERSK MC-KINNEY MOLLER">
                                🚢 Theo dõi tàu Maersk về Đà Nẵng
                            </button>
                        </div>
                    </div>
                </div>

                <div class="drawer-footer">
                    <div class="drawer-input-row">
                        <textarea id="drawer-textarea" class="drawer-textarea" placeholder="Hỏi nhanh AI Logistics... (Enter gửi)" rows="1"></textarea>
                        <button id="btn-drawer-send" class="drawer-btn-send" disabled title="Gửi">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
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

        // Close Drawer
        $('#btn-drawer-close').on('click', function () {
            $drawer.fadeOut(150);
        });

        // Fullscreen action -> Navigate to Page
        $('#btn-drawer-fullscreen').on('click', function () {
            if (typeof frappe !== 'undefined' && frappe.set_route) {
                frappe.set_route('logistics-ai-chatbot');
                $drawer.fadeOut(150);
            } else {
                window.location.href = '/app/logistics-ai-chatbot';
            }
        });

        // Auto-expand textarea
        $textarea.on('input', function () {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
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
            const $assistantRow = appendMessage('assistant', '<span class="typing-dots">● ● ●</span>');

            // 3. Dispatch to Bridge or Default Mock
            if (window.LogisticsChatbotBridge && typeof window.LogisticsChatbotBridge.onSendMessage === 'function') {
                window.LogisticsChatbotBridge.onSendMessage(
                    text,
                    [],
                    { drawer: true },
                    {
                        onThinking: (t) => {
                            if (!$assistantRow.find('.drawer-thinking-mini').length) {
                                $assistantRow.find('.drawer-msg-bubble').prepend(`<div class="drawer-thinking-mini">💡 ${frappe.utils.escape_html(t.slice(0, 75))}...</div>`);
                            }
                        },
                        onToolCall: (name) => {
                            $assistantRow.find('.drawer-msg-bubble').prepend(`<div class="drawer-thinking-mini">⚡ Gọi Tool: <code>${frappe.utils.escape_html(name)}</code></div>`);
                        },
                        onStreamChunk: (chunk) => {
                            $assistantRow.find('.drawer-msg-bubble').html(formatMiniMarkdown(chunk));
                            scrollToBottom();
                        },
                        onComplete: (finalText) => {
                            $assistantRow.find('.drawer-msg-bubble').html(formatMiniMarkdown(finalText));
                            scrollToBottom();
                        },
                        onError: (err) => {
                            $assistantRow.find('.drawer-msg-bubble').html(`<span style="color:#ef4444;">⚠️ Lỗi: ${frappe.utils.escape_html(err)}</span>`);
                            scrollToBottom();
                        }
                    }
                );
            } else {
                // Default fast responder
                setTimeout(() => {
                    let reply = '';
                    const lower = text.toLowerCase();
                    if (lower.includes('cost') || lower.includes('giá vốn') || lower.includes('chi phí') || lower.includes('imp-2026-001')) {
                        reply = `<strong>📊 Hồ sơ IMP-2026-001:</strong><br>- Chi phí thực tế: <strong>$18,350.00</strong> (Vượt $1,550 so với dự toán $16,800).<br>- Tỷ lệ phụ phí: <strong>14.68%</strong>.<br>- Trạng thái LCV: Đã đồng bộ sang <strong>LCV-2026-0004</strong>.<br>👉 Bấm nút ⤢ góc trên để xem chi tiết đầy đủ!`;
                    } else if (lower.includes('tàu') || lower.includes('maersk') || lower.includes('vessel')) {
                        reply = `<strong>🚢 Tàu MAERSK MC-KINNEY MOLLER:</strong><br>- Vị trí: Vịnh Đà Nẵng (16.1284° N, 108.2391° E).<br>- Vận tốc: 14.8 kts.<br>- ETA: <strong>14:00 ngày 18/10/2026</strong> tại Cảng Tiên Sa.`;
                    } else {
                        reply = `Tôi đã nhận câu hỏi: <em>"${frappe.utils.escape_html(text)}"</em>.<br>Hệ thống AI Copilot đã sẵn sàng nhận cấu hình API từ bạn.`;
                    }
                    $assistantRow.find('.drawer-msg-bubble').html(reply);
                    scrollToBottom();
                }, 600);
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

        function formatMiniMarkdown(text) {
            if (!text) return '';
            let formatted = frappe.utils.escape_html(text);
            formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
            formatted = formatted.replace(/\n/g, '<br>');
            return formatted;
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
})();
