(()=>{console.log("SMART WORKFLOW WIDGET SCRIPT LOADED");function ct(){let R=[{doctype:"Material Request",id:"wiz-Material-Request",slug:"material-request",label:"1. Y\xEAu c\u1EA7u mua h\xE0ng (Material Request)"},{doctype:"Purchase Order",id:"wiz-Purchase-Order",slug:"purchase-order",label:"2. \u0110\u01A1n \u0111\u1EB7t h\xE0ng (Purchase Order)"},{doctype:"Payment Entry",id:"wiz-Payment-Entry",slug:"payment-entry",label:"3. \u0110\u1EB7t c\u1ECDc / T\u1EA1m \u1EE9ng (Payment Entry)"},{doctype:"Shipment Tracking",id:"wiz-Shipment-Tracking",slug:"managementLogistic",label:"4. Theo d\xF5i h\xE0nh tr\xECnh (Shipment Tracking)"},{doctype:"Purchase Receipt",id:"wiz-Purchase-Receipt",slug:"purchase-receipt",label:"5. Nh\u1EADn h\xE0ng (Purchase Receipt)"},{doctype:"Landed Cost Voucher",id:"wiz-Landed-Cost-Voucher",slug:"landed-cost-voucher",label:"6. Ph\xE2n b\u1ED5 gi\xE1 v\u1ED1n (Landed Cost)"},{doctype:"Stock Entry",id:"wiz-Stock-Entry",slug:"stock-entry",label:"7. Nh\u1EADp kho (Stock Entry)"}],N=[{doctype:"Sales Order",id:"wiz-exp-Sales-Order",slug:"sales-order",label:"1. \u0110\u01A1n b\xE1n h\xE0ng (Sales Order)"},{doctype:"Payment Entry",id:"wiz-exp-Payment-Entry-Deposit",slug:"payment-entry",label:"2. Thu ti\u1EC1n c\u1ECDc (Payment Entry)"},{doctype:"Stock Entry",id:"wiz-exp-Stock-Entry",slug:"stock-entry",label:"3. Chuy\u1EC3n kho c\u1EA3ng (Stock Entry)"},{doctype:"Delivery Note",id:"wiz-exp-Delivery-Note",slug:"delivery-note",label:"4. Xu\u1EA5t kho giao h\xE0ng (Delivery Note)"},{doctype:"Shipment Tracking",id:"wiz-exp-Shipment-Tracking",slug:"managementLogistic",label:"5. Theo d\xF5i h\xE0nh tr\xECnh (Shipment Tracking)"},{doctype:"Sales Invoice",id:"wiz-exp-Sales-Invoice",slug:"sales-invoice",label:"6. H\xF3a \u0111\u01A1n th\u01B0\u01A1ng m\u1EA1i (Sales Invoice)"},{doctype:"Payment Entry",id:"wiz-exp-Payment-Entry-Final",slug:"payment-entry",label:"7. T\u1EA5t to\xE1n ngo\u1EA1i t\u1EC7 (Payment Entry)"}],_t=R,Q=["Material Request","Purchase Order","Purchase Receipt","Landed Cost Voucher"],q=["Sales Order","Delivery Note","Sales Invoice"],dt=["Payment Entry","Shipment Tracking","Stock Entry"],K=Array.from(new Set([...Q,...q,...dt])),kt=K,B="import",s=null,J=null,L=[],y=null,m=null;$(document).on("click",".leaflet-popup-close-button",function(t){return t.preventDefault(),t.stopPropagation(),t.stopImmediatePropagation(),s&&s.closePopup(),!1});function tt(t){return t==="Air"?`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#007AFF" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1.5C11.2 1.5 10.6 2.3 10.6 3.2V8.8L2.4 13.5C1.8 13.8 1.5 14.5 1.5 15.1C1.5 15.9 2.2 16.5 3 16.5H10.6V20.2L8.2 21.8C7.9 22 7.7 22.3 7.7 22.7C7.7 23.4 8.3 24 9 24H15C15.7 24 16.3 23.4 16.3 22.7C16.3 22.3 16.1 22 15.8 21.8L13.4 20.2V16.5H21C21.8 16.5 22.5 15.9 22.5 15.1C22.5 14.5 22.2 13.8 21.6 13.5L13.4 8.8V3.2C13.4 2.3 12.8 1.5 12 1.5Z" stroke="#0047AB" stroke-width="0.5"/>
                </svg>
            `:t==="Ocean"?`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1 C14.8 3.5 18 8 18 14 V20 C18 21.7 16.7 23 15 23 H9 C7.3 23 6 21.7 6 20 V14 C6 8 9.2 3.5 12 1 Z" fill="#0055B3" stroke="#003380" stroke-width="0.8"/>
                    <rect x="8" y="6.5" width="8" height="2.2" rx="0.4" fill="#38BDF8"/>
                    <rect x="8" y="9.7" width="8" height="2.2" rx="0.4" fill="#BAE6FD"/>
                    <rect x="8" y="12.9" width="8" height="2.2" rx="0.4" fill="#38BDF8"/>
                    <rect x="8" y="16.1" width="8" height="2.2" rx="0.4" fill="#BAE6FD"/>
                    <rect x="8.5" y="19.2" width="7" height="2.6" rx="0.5" fill="#FFFFFF"/>
                    <rect x="10.5" y="20" width="3" height="1" fill="#0055B3"/>
                </svg>
            `:`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="6" y="8.5" width="12" height="14" rx="1.2" fill="#EA580C" stroke="#C2410C" stroke-width="0.6"/>
                    <line x1="7.5" y1="11.5" x2="16.5" y2="11.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <line x1="7.5" y1="14.5" x2="16.5" y2="14.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <line x1="7.5" y1="17.5" x2="16.5" y2="17.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <line x1="7.5" y1="20.5" x2="16.5" y2="20.5" stroke="#FFEDD5" stroke-width="0.8"/>
                    <rect x="7" y="1.5" width="10" height="5.8" rx="1.5" fill="#C2410C"/>
                    <rect x="8.5" y="2.5" width="7" height="2" rx="0.5" fill="#FEF08A"/>
                    <rect x="5.2" y="3" width="1.5" height="1" rx="0.3" fill="#C2410C"/>
                    <rect x="17.3" y="3" width="1.5" height="1" rx="0.3" fill="#C2410C"/>
                </svg>
            `}function et(t){return t==="Ocean"||t==="seaport"||t==="port"?`
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0055B3" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="5" r="3"/>
                    <line x1="12" y1="22" x2="12" y2="8"/>
                    <path d="M5 12H2a10 10 0 0 0 20 0h-3"/>
                </svg>
            `:`
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.2-1.1.6L2.5 8l6.4 3.3L7 15l-3.3-1.1-1.2 1.3 4.2 3.8 3.8 4.2 1.3-1.2L10.7 18.7l3.7-1.9 3.3 6.4 1.2-1.2-.4-2.6Z"/>
                </svg>
            `}function ht(){$("#lw-smart-widget-styles").length===0&&$("head").append(`
                <style id="lw-smart-widget-styles">
                    #lw-fab-container {
                        position: fixed !important;
                        bottom: 32px !important;
                        left: 32px !important;
                        z-index: 9999 !important;
                        display: flex !important;
                        flex-direction: column-reverse !important;
                        align-items: center !important;
                        gap: 14px !important;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
                    }
                    .lw-fab {
                        width: 58px !important;
                        height: 58px !important;
                        border-radius: 50% !important;
                        background: rgba(255, 255, 255, 0.94) !important;
                        backdrop-filter: blur(25px) !important;
                        -webkit-backdrop-filter: blur(25px) !important;
                        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12), 0 2px 6px rgba(0, 0, 0, 0.06), inset 0 1px 1px #ffffff !important;
                        border: 1px solid rgba(226, 232, 240, 0.9) !important;
                        display: flex !important;
                        justify-content: center !important;
                        align-items: center !important;
                        cursor: pointer !important;
                        position: relative !important;
                        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                        padding: 0 !important;
                        margin: 0 !important;
                        outline: none !important;
                    }
                    .lw-fab:hover {
                        transform: scale(1.08) translateY(-2px) !important;
                        background: #ffffff !important;
                        box-shadow: 0 14px 32px rgba(0, 0, 0, 0.16), inset 0 1px 1px #ffffff !important;
                    }
                    .lw-fab:active {
                        transform: scale(0.95) !important;
                    }
                    .lw-fab.active {
                        background: #f1f5f9 !important;
                        border-color: #cbd5e1 !important;
                    }
                    .lw-fab .fab-icon {
                        position: absolute !important;
                        width: 32px !important;
                        height: 32px !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                        pointer-events: none !important;
                        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                    }
                    .lw-fab:hover .fab-icon svg {
                        transform: scale(1.08) rotate(12deg) !important;
                    }
                    .lw-fab.active .fab-icon {
                        opacity: 0 !important;
                        transform: scale(0.3) rotate(-90deg) !important;
                    }
                    .lw-fab .fab-close-icon {
                        position: absolute !important;
                        color: #475569 !important;
                        font-size: 22px !important;
                        font-weight: 400 !important;
                        line-height: 1 !important;
                        opacity: 0 !important;
                        transform: scale(0.3) rotate(-90deg) !important;
                        transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                        pointer-events: none !important;
                        display: flex !important;
                        align-items: center !important;
                        justify-content: center !important;
                    }
                    .lw-fab.active .fab-close-icon {
                        opacity: 1 !important;
                        transform: scale(1) rotate(0deg) !important;
                    }
                    #lw-fab-menu {
                        display: flex !important;
                        flex-direction: column-reverse !important;
                        gap: 12px !important;
                        pointer-events: none !important;
                    }
                    #lw-fab-menu.show {
                        pointer-events: auto !important;
                    }
                    .lw-sub-fab {
                        width: 48px !important;
                        height: 48px !important;
                        border-radius: 50% !important;
                        background: rgba(255, 255, 255, 0.95) !important;
                        backdrop-filter: blur(20px) !important;
                        -webkit-backdrop-filter: blur(20px) !important;
                        border: 1px solid rgba(226, 232, 240, 0.9) !important;
                        color: #0f172a !important;
                        display: flex !important;
                        justify-content: center !important;
                        align-items: center !important;
                        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
                        cursor: pointer !important;
                        position: relative !important;
                        opacity: 0 !important;
                        transform: translateY(16px) scale(0.8) !important;
                        transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                    }
                    #lw-fab-menu.show .lw-sub-fab:nth-child(1) { transition-delay: 0.04s; opacity: 1 !important; transform: translateY(0) scale(1) !important; }
                    #lw-fab-menu.show .lw-sub-fab:nth-child(2) { transition-delay: 0.08s; opacity: 1 !important; transform: translateY(0) scale(1) !important; }
                    #lw-fab-menu.show .lw-sub-fab:nth-child(3) { transition-delay: 0.12s; opacity: 1 !important; transform: translateY(0) scale(1) !important; }
                    .lw-sub-fab:hover {
                        background: #ffffff !important;
                        transform: scale(1.1) !important;
                        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12) !important;
                    }
                    .lw-sub-fab::after {
                        content: attr(data-tooltip);
                        position: absolute;
                        left: 100%;
                        margin-left: 12px;
                        background: rgba(15, 23, 42, 0.88);
                        backdrop-filter: blur(15px);
                        -webkit-backdrop-filter: blur(15px);
                        color: #ffffff;
                        padding: 6px 12px;
                        border-radius: 6px;
                        font-size: 12px;
                        font-weight: 500;
                        white-space: nowrap;
                        pointer-events: none;
                        opacity: 0;
                        transform: translateX(-6px) scale(0.95);
                        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    }
                    .lw-sub-fab:hover::after {
                        opacity: 1;
                        transform: translateX(0) scale(1);
                    }
                    .lw-popup {
                        position: fixed !important;
                        bottom: 32px !important;
                        left: 104px !important;
                        width: 360px !important;
                        max-width: calc(100vw - 120px) !important;
                        background: rgba(255, 255, 255, 0.98) !important;
                        backdrop-filter: blur(25px) !important;
                        -webkit-backdrop-filter: blur(25px) !important;
                        border-radius: 18px !important;
                        border: 1px solid rgba(226, 232, 240, 0.9) !important;
                        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15), 0 4px 12px rgba(0, 0, 0, 0.05) !important;
                        z-index: 1040 !important;
                        display: none;
                        overflow: hidden !important;
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
                        animation: lwPopupFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
                    }
                    @keyframes lwPopupFadeIn {
                        from { opacity: 0; transform: scale(0.96) translateY(8px); }
                        to { opacity: 1; transform: scale(1) translateY(0); }
                    }
                    .lw-popup-large {
                        width: 680px !important;
                        max-width: calc(100vw - 120px) !important;
                    }
                    .lw-popup-header {
                        padding: 12px 16px !important;
                        background: #f8fafc !important;
                        border-bottom: 1px solid #e2e8f0 !important;
                        font-weight: 700 !important;
                        font-size: 13.5px !important;
                        color: #0f172a !important;
                        display: flex !important;
                        justify-content: space-between !important;
                        align-items: center !important;
                    }
                    .lw-popup-close {
                        color: #94a3b8 !important;
                        cursor: pointer !important;
                        font-size: 14px !important;
                        padding: 4px 6px !important;
                        border-radius: 4px !important;
                        transition: all 0.15s ease !important;
                    }
                    .lw-popup-close:hover {
                        color: #0f172a !important;
                        background: #e2e8f0 !important;
                    }
                    .lw-popup-body {
                        padding: 16px !important;
                        max-height: 72vh !important;
                        overflow-y: auto !important;
                    }
                </style>
            `)}function j(){if(ht(),$("#lw-fab-container").length===0){let t=`
                <div id="lw-fab-container" style="position: fixed !important; bottom: 32px !important; left: 32px !important; z-index: 9999 !important;">
                    <button class="lw-fab" id="lw-fab-main" title="Tr\u1EE3 l\xFD Logistics & H\u1ED7 tr\u1EE3">
                        <span class="fab-icon">
                            <svg class="lw-lifebuoy-svg" viewBox="0 0 24 24" width="30" height="30" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <defs>
                                    <linearGradient id="lw-apple-blue-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                        <stop offset="0%" stop-color="#0A84FF"/>
                                        <stop offset="50%" stop-color="#0071E3"/>
                                        <stop offset="100%" stop-color="#0055D4"/>
                                    </linearGradient>
                                    <filter id="lw-liquid-glow" x="-20%" y="-20%" width="140%" height="140%">
                                        <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-color="#0071E3" flood-opacity="0.3"/>
                                    </filter>
                                </defs>
                                <g filter="url(#lw-liquid-glow)">
                                    <circle cx="12" cy="12" r="9.2" stroke="url(#lw-apple-blue-grad)" stroke-width="2.3"/>
                                    <circle cx="12" cy="12" r="3.8" stroke="url(#lw-apple-blue-grad)" stroke-width="2.3"/>
                                    <line x1="5.5" y1="5.5" x2="9.3" y2="9.3" stroke="url(#lw-apple-blue-grad)" stroke-width="2.3" stroke-linecap="round"/>
                                    <line x1="18.5" y1="5.5" x2="14.7" y2="9.3" stroke="url(#lw-apple-blue-grad)" stroke-width="2.3" stroke-linecap="round"/>
                                    <line x1="18.5" y1="18.5" x2="14.7" y2="14.7" stroke="url(#lw-apple-blue-grad)" stroke-width="2.3" stroke-linecap="round"/>
                                    <line x1="5.5" y1="18.5" x2="9.3" y2="14.7" stroke="url(#lw-apple-blue-grad)" stroke-width="2.3" stroke-linecap="round"/>
                                </g>
                            </svg>
                        </span>
                        <span class="fab-close-icon">\u2715</span>
                    </button>
                    <div id="lw-fab-menu">
                        <button class="lw-fab lw-sub-fab" id="lw-fab-workflow" data-tooltip="Ti\u1EBFn tr\xECnh (Workflow)">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                                <path d="M9 12h6"/>
                                <path d="M9 16h6"/>
                            </svg>
                        </button>
                        <button class="lw-fab lw-sub-fab" id="lw-fab-shipment" data-tooltip="H\xE0nh tr\xECnh (Shipment)">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="1" y="3" width="15" height="13" rx="2" ry="2"/>
                                <polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
                                <circle cx="5.5" cy="18.5" r="2.5"/>
                                <circle cx="18.5" cy="18.5" r="2.5"/>
                            </svg>
                        </button>
                        <button class="lw-fab lw-sub-fab" id="lw-fab-ai" data-tooltip="AI Chat">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="11" width="18" height="10" rx="2"/>
                                <circle cx="12" cy="5" r="2"/>
                                <path d="M12 7v4"/>
                                <line x1="8" y1="16" x2="8" y2="16"/>
                                <line x1="16" y1="16" x2="16" y2="16"/>
                            </svg>
                        </button>
                    </div>
                </div>

                <!-- Popup: Workflow (Nh\u1EADp kh\u1EA9u / Xu\u1EA5t kh\u1EA9u) -->
                <div class="lw-popup" id="lw-popup-workflow">
                    <div class="lw-popup-header" style="display: flex; justify-content: space-between; align-items: center; padding: 12px 16px;">
                        <span>Ti\u1EBFn tr\xECnh ch\u1EE9ng t\u1EEB XNK</span>
                        <span class="lw-popup-close" data-target="#lw-popup-workflow" style="cursor: pointer;">\u2716</span>
                    </div>
                    <!-- Tab Switcher: Nh\u1EADp Kh\u1EA9u | Xu\u1EA5t Kh\u1EA9u (Apple Clean Style - No Purple) -->
                    <div class="lw-workflow-tab-bar" style="display: flex; background: #eef2f6; padding: 4px; margin: 8px 14px 4px 14px; border-radius: 8px; gap: 4px;">
                        <button type="button" class="lw-tab-btn active" id="lw-tab-import" data-flow="import" style="flex: 1; border: none; outline: none; background: #ffffff; color: #0071E3; font-weight: 600; font-size: 12px; padding: 6px 10px; border-radius: 6px; cursor: pointer; box-shadow: 0 1px 3px rgba(0,0,0,0.08); transition: all 0.2s;">
                            Nh\u1EADp Kh\u1EA9u
                        </button>
                        <button type="button" class="lw-tab-btn" id="lw-tab-export" data-flow="export" style="flex: 1; border: none; outline: none; background: transparent; color: #495057; font-weight: 500; font-size: 12px; padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                            Xu\u1EA5t Kh\u1EA9u
                        </button>
                    </div>
                    <div class="lw-popup-body" style="padding: 10px 14px 14px 14px;">
                        <!-- Danh s\xE1ch Nh\u1EADp kh\u1EA9u -->
                        <ul class="lw-step-list" id="lw-import-step-list">
                            ${R.map(e=>`
                                <li class="lw-step-item" id="${e.id}">
                                    <span class="wiz-check-badge"></span>
                                    <a href="/app/${e.slug}">${e.label}</a>
                                </li>
                            `).join("")}
                        </ul>
                        <!-- Danh s\xE1ch Xu\u1EA5t kh\u1EA9u -->
                        <ul class="lw-step-list" id="lw-export-step-list" style="display: none;">
                            ${N.map(e=>`
                                <li class="lw-step-item" id="${e.id}">
                                    <span class="wiz-check-badge"></span>
                                    <a href="/app/${e.slug}">${e.label}</a>
                                </li>
                            `).join("")}
                        </ul>
                    </div>
                </div>

                <!-- Popup: Shipment (Map & Timeline) -->
                <div class="lw-popup lw-popup-large" id="lw-popup-shipment">
                    <div class="lw-popup-header" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; gap: 8px;">
                        <span style="font-weight: 600; font-size: 13px; display: inline-flex; align-items: center; gap: 6px;">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="10"/>
                                <line x1="2" y1="12" x2="22" y2="12"/>
                                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                            </svg>
                            B\u1EA3n \u0111\u1ED3 & H\xE0nh tr\xECnh V\u1EADn chuy\u1EC3n To\xE0n c\u1EA7u
                        </span>
                        <span class="lw-popup-close" data-target="#lw-popup-shipment" style="cursor: pointer; font-size: 13px; padding: 2px 4px; margin-left: auto;">\u2716</span>
                    </div>
                    <div class="lw-popup-body" id="lw-shipment-content">
                        <div style="text-align: center; color: #8d99a6; padding: 25px 0;">
                            \u0110ang t\u1EA3i th\xF4ng tin h\xE0nh tr\xECnh...
                        </div>
                    </div>
                </div>

                <!-- Popup: AI Chat -->
                <div class="lw-popup" id="lw-popup-ai">
                    <div class="lw-popup-header">
                        Tr\u1EE3 l\xFD AI Logistics & H\u1EA3i quan
                        <span class="lw-popup-close" data-target="#lw-popup-ai">\u2716</span>
                    </div>
                    <div class="lw-popup-body" style="text-align: center; padding: 30px 15px;">
                        <div style="margin-bottom: 12px;">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0071E3" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="11" width="18" height="10" rx="2"/>
                                <circle cx="12" cy="5" r="2"/>
                                <path d="M12 7v4"/>
                                <line x1="8" y1="16" x2="8" y2="16"/>
                                <line x1="16" y1="16" x2="16" y2="16"/>
                            </svg>
                        </div>
                        <h4 style="margin:0 0 10px 0; color: #1f272e;">Tr\u1EE3 l\xFD RAG H\u1EA3i quan</h4>
                        <p style="color: #6c757d; font-size: 13px; line-height: 1.5; margin: 0;">
                            H\u1EC7 th\u1ED1ng AI RAG h\u1ED7 tr\u1EE3 tra c\u1EE9u v\u0103n b\u1EA3n ph\xE1p lu\u1EADt H\u1EA3i quan v\xE0 \u0111\u1EC1 xu\u1EA5t m\xE3 HS Code \u0111ang k\u1EBFt n\u1ED1i!
                        </p>
                    </div>
                </div>
            `;$("body").append(t),$("#lw-fab-main").on("click",function(){$(this).toggleClass("active"),$(this).hasClass("active")?$("#lw-fab-menu").addClass("show"):($("#lw-fab-menu").removeClass("show"),$(".lw-popup").hide())}),$(".lw-sub-fab").on("click",function(e){let o=$(this).attr("id"),n=o.replace("lw-fab-","lw-popup-");$(".lw-popup").hide(),$("#"+n).show(),o==="lw-fab-shipment"&&ut()}),$(document).on("click","#lw-btn-open-full-hub",function(e){e.preventDefault(),$(".lw-popup").hide(),$("#lw-fab-menu").removeClass("show"),$("#lw-fab-main").removeClass("active");let o=typeof frappe!="undefined"&&frappe.get_route?frappe.get_route():[],n={tab:"tracking"};o&&o[0]==="Form"&&["Purchase Order","Shipment Tracking","Purchase Receipt"].includes(o[1])&&o[2]&&(n.shipment=o[2],n.doctype=o[1]),typeof frappe!="undefined"&&frappe.set_route?(frappe.route_options=n,frappe.set_route("managementLogistic")):window.location.href="/app/managementLogistic"+(n.shipment?"?shipment="+encodeURIComponent(n.shipment):"")}),$(document).on("click","#wiz-Shipment-Tracking a, #wiz-exp-Shipment-Tracking a",function(e){typeof frappe!="undefined"&&frappe.set_route&&(e.preventDefault(),$(".lw-popup").hide(),$("#lw-fab-menu").removeClass("show"),$("#lw-fab-main").removeClass("active"),frappe.route_options={tab:"tracking"},frappe.set_route("managementLogistic"))}),$(document).on("click",".lw-tab-btn",function(e){e.preventDefault();let o=$(this).data("flow");Y(o,!0)}),$(".lw-popup-close").on("click",function(){if($($(this).data("target")).hide(),m&&(cancelAnimationFrame(m),m=null),s){try{s.remove()}catch(e){}s=null,y=null}})}}function ut(){it()}function it(t="active"){let e=$("#lw-shipment-content"),o=`
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 8px;">
                <div style="flex: 1; min-width: 0;">
                    <strong style="color: #1f272e; font-size: 13.5px;">Danh s\xE1ch L\xF4 h\xE0ng Qu\u1ED1c t\u1EBF:</strong>
                    <div style="font-size: 11px; color: #6c757d; margin-top: 2px;">Nh\u1EA5n v\xE0o \u0111\u01A1n h\xE0ng \u0111\u1EC3 xem b\u1EA3n \u0111\u1ED3 l\u1ED9 tr\xECnh tr\u1EF1c ti\u1EBFp:</div>
                </div>
                <div style="flex-shrink: 0;">
                    <select id="lw-filter-status" class="form-control" style="font-size: 11.5px; height: 28px; border-radius: 6px; border: 1px solid #ced4da; background-color: #ffffff; padding: 1px 6px; cursor: pointer; min-width: 145px; font-weight: 500; color: #1f272e; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <option value="active" ${t==="active"?"selected":""}>\u0110ang v\u1EADn chuy\u1EC3n</option>
                        <option value="completed" ${t==="completed"?"selected":""}>\u0110\xE3 ho\xE0n th\xE0nh</option>
                        <option value="customs" ${t==="customs"?"selected":""}>\u0110ang th\xF4ng quan</option>
                        <option value="all" ${t==="all"?"selected":""}>T\u1EA5t c\u1EA3 \u0111\u01A1n h\xE0ng</option>
                    </select>
                </div>
            </div>
            <div id="lw-shipment-items-container">
                <div style="text-align: center; padding: 25px; color: #6c757d;">
                    <div class="spinner-border text-primary" role="status" style="width: 1.8rem; height: 1.8rem;"></div>
                    <div style="margin-top: 8px; font-size: 12px;">\u0110ang t\u1EA3i danh s\xE1ch l\xF4 h\xE0ng...</div>
                </div>
            </div>
        `;e.html(o),$("#lw-filter-status").on("change",function(){let n=$(this).val();nt(n)}),nt(t)}function nt(t){let e=$("#lw-shipment-items-container");e.html(`
            <div style="text-align: center; padding: 25px; color: #6c757d;">
                <div class="spinner-border text-primary" role="status" style="width: 1.8rem; height: 1.8rem;"></div>
                <div style="margin-top: 8px; font-size: 12px;">\u0110ang l\u1ECDc danh s\xE1ch \u0111\u01A1n h\xE0ng...</div>
            </div>
        `),frappe.call({method:"logistics_wizard.api.get_active_shipments",args:{status_filter:t},callback:function(o){if(o.message&&o.message.status==="success"){let n=o.message.data||[];if(n.length===0){let i=t==="active"?"\u0111ang v\u1EADn chuy\u1EC3n":t==="completed"?"\u0111\xE3 ho\xE0n th\xE0nh":t==="customs"?"\u0111ang l\xE0m th\u1EE7 t\u1EE5c th\xF4ng quan":"";e.html(`
                            <div style="text-align: center; padding: 35px 20px; color: #8d99a6;">
                                <div style="margin-bottom: 8px;">
                                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                                        <line x1="12" y1="22.08" x2="12" y2="12"/>
                                    </svg>
                                </div>
                                <strong style="color: #475569;">Kh\xF4ng c\xF3 \u0111\u01A1n h\xE0ng n\xE0o ${i}.</strong>
                                <p style="font-size: 12px; margin-top: 6px;">H\xE3y th\u1EED ch\u1ECDn b\u1ED9 l\u1ECDc kh\xE1c (v\xED d\u1EE5 "T\u1EA5t c\u1EA3 \u0111\u01A1n h\xE0ng") \u0111\u1EC3 xem t\u1EA5t c\u1EA3.</p>
                            </div>
                        `);return}let l='<div class="lw-shipment-list" style="display: flex; flex-direction: column; gap: 8px;">';n.forEach(i=>{let a="#e7f1ff",r="#0071E3";i.is_completed||i.status==="Completed"?(a="#e6f4ea",r="#137333"):i.is_customs||i.status==="Customs Clearance"?(a="#fef7e0",r="#b06000"):i.status==="Draft"&&(a="#f1f3f4",r="#5f6368");let c=i.shipping_method==="Air"?"H\xE0ng kh\xF4ng":i.shipping_method==="Ocean"?"\u0110\u01B0\u1EDDng bi\u1EC3n":"\u0110\u01B0\u1EDDng b\u1ED9",p=i.origin_port&&i.destination_port?` &bull; ${i.origin_port} \u2192 ${i.destination_port}`:"";l+=`
                            <div class="lw-shipment-item" data-name="${i.name}" data-shipment="${i.shipment_tracking||i.name}" style="padding: 12px 14px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; cursor: pointer; transition: all 0.2s;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong style="color: #0071E3; font-size: 13px;">${i.name}</strong>
                                        <span style="font-size: 11px; color: #6c757d; margin-left: 6px;">[${c}]${p}</span>
                                    </div>
                                    <span class="badge" style="background: ${a}; color: ${r}; font-weight: 600; font-size: 11px; padding: 4px 8px; border-radius: 4px;">
                                        ${i.status}
                                    </span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #495057; margin-top: 5px;">
                                    <div><strong>Nh\xE0 cung c\u1EA5p:</strong> ${i.supplier_name||"N/A"}</div>
                                    <div>
                                        ${i.shipment_tracking?`<span style="color: #6c757d; font-size: 11px;">V\u1EADn \u0111\u01A1n: <strong style="color: #0071E3;">${i.shipment_tracking}</strong></span>`:""}
                                    </div>
                                </div>
                            </div>
                        `}),l+="</div>",e.html(l),$(".lw-shipment-item").hover(function(){$(this).css({background:"#eef5ff","border-color":"#0071E3"})},function(){$(this).css({background:"#f8f9fa","border-color":"#e9ecef"})}).on("click",function(){let i=$(this).data("shipment")||$(this).data("name");if($(".lw-popup").hide(),$("#lw-fab-menu").removeClass("show"),$("#lw-fab-main").removeClass("active"),typeof frappe!="undefined"&&frappe.set_route){let a=frappe.get_route_str?frappe.get_route_str():"";(a==="managementLogistic"||a==="manageLogistic")&&frappe.pages.managementLogistic&&frappe.pages.managementLogistic.shipment_tracking_hub?frappe.pages.managementLogistic.switch_to_tab?frappe.pages.managementLogistic.switch_to_tab("tracking",i):frappe.pages.managementLogistic.shipment_tracking_hub.select_shipment(i):(frappe.route_options={shipment:i,tab:"tracking"},frappe.set_route("managementLogistic"))}else window.location.href="/app/managementLogistic?shipment="+encodeURIComponent(i)})}else e.html('<div style="text-align: center; color: red; padding: 20px;">L\u1ED7i t\u1EA3i danh s\xE1ch v\u1EADn chuy\u1EC3n.</div>')}})}function $t(t,e){$("#lw-shipment-content").html(`
            <div class="lw-map-panel">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <button class="btn btn-xs btn-default" id="lw-btn-back-shipments">\u2190 Quay l\u1EA1i danh s\xE1ch</button>
                    <div style="text-align: right;">
                        <span style="font-size: 11px; color: #6c757d;">${e}:</span>
                        <strong style="color: #007AFF; font-size: 13px; margin-left: 4px;">${t}</strong>
                    </div>
                </div>

                <!-- Map Container -->
                <div id="shipment-map" style="width: 100%; height: 350px; border-radius: 10px; background: #e5e5ea; border: 1px solid #ced4da;"></div>

                <!-- Info Box -->
                <div class="lw-map-info" id="lw-map-info-text" style="padding: 10px 14px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; font-size: 13px;">
                    <span class="text-muted">\u0110ang ph\xE2n t\xEDch d\u1EEF li\u1EC7u t\u1ECDa \u0111\u1ED9 \u0111\u1ECBa l\xFD v\xE0 d\u1EF1ng l\u1ED9 tr\xECnh...</span>
                </div>

                <!-- Detailed Timeline -->
                <div>
                    <div style="font-weight: 600; font-size: 13px; color: #343a40; margin-bottom: 8px;">
                        L\u1ED9 tr\xECnh V\u1EADn chuy\u1EC3n Chi ti\u1EBFt (Transit Checkpoints):
                    </div>
                    <div id="lw-timeline-container" style="margin-top: 6px;"></div>
                </div>
            </div>
        `),$("#lw-btn-back-shipments").on("click",function(){if(m&&(cancelAnimationFrame(m),m=null),s){try{s.remove()}catch(n){}s=null,y=null}it()}),frappe.call({method:"logistics_wizard.api.get_shipment_tracking",args:{docname:t,doctype:e},callback:function(n){n.message&&n.message.status==="success"?ft(n.message.data,t,e):$("#lw-map-info-text").html(`<span style="color: #d9534f;">${n.message?n.message.message:"Kh\xF4ng th\u1EC3 t\u1EA3i th\xF4ng tin l\u1ED9 tr\xECnh."}</span>`)}})}function ot(t){let e=window.L||window.leaflet;if(!e||!s)return;t==="Ocean"||t==="Sea"?(y||(y=e.tileLayer("https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",{attribution:'Map data: &copy; <a href="http://www.openseamap.org">OpenSeaMap</a> contributors',maxZoom:18,opacity:1})),s.hasLayer(y)||y.addTo(s)):y&&s.hasLayer(y)&&s.removeLayer(y)}function rt(t,e,o){let[n,l]=t,[i,a]=e,[r,c]=o,p=c-a,d=r-i;p>180&&(p-=360),p<-180&&(p+=360);let u=l-a,k=n-i;u>180&&(u-=360),u<-180&&(u+=360);let v=p*p+d*d;if(v===0)return Math.hypot(u,k);let x=Math.max(0,Math.min(1,(u*p+k*d)/v)),P=x*p,b=x*d;return Math.hypot(u-P,k-b)}function I(t,e=.002){if(!t||!Array.isArray(t)||t.length<=2)return t||[];let o=0,n=0,l=t.length-1;for(let i=1;i<l;i++){let a=rt(t[i],t[0],t[l]);a>o&&(o=a,n=i)}if(o>e){let i=I(t.slice(0,n+1),e),a=I(t.slice(n),e);return i.slice(0,i.length-1).concat(a)}else return[t[0],t[l]]}function at(t,e,o,n){let l=Math.PI/180,i=180/Math.PI,a=t*l,r=o*l,c=(n-e)*l;for(;c>Math.PI;)c-=2*Math.PI;for(;c<-Math.PI;)c+=2*Math.PI;let p=Math.sin(c)*Math.cos(r),d=Math.cos(a)*Math.sin(r)-Math.sin(a)*Math.cos(r)*Math.cos(c);return(Math.atan2(p,d)*i+360)%360}function V(t){let e=[0],o=0;if(!t||t.length<=1)return{cumulative:[0],total:0};for(let n=0;n<t.length-1;n++){let[l,i]=t[n],[a,r]=t[n+1],c=r-i;c>180&&(c-=360),c<-180&&(c+=360);let p=a-l,d=Math.cos((l+a)/2*Math.PI/180);o+=Math.hypot(p,c*d),e.push(o)}return{cumulative:e,total:o}}function W(t,e,o){if(!t||t.length===0)return{point:[0,0],bearing:0};if(t.length===1)return{point:t[0],bearing:0};let n=Math.max(0,Math.min(1,o));if(e.total===0)return{point:t[0],bearing:0};let l=n*e.total,i=0;for(let g=0;g<e.cumulative.length-1;g++)if(l>=e.cumulative[g]&&l<=e.cumulative[g+1]){i=g;break}i>=t.length-1&&(i=t.length-2);let a=e.cumulative[i],r=e.cumulative[i+1]-a,c=r===0?0:Math.max(0,Math.min(1,(l-a)/r)),p=t[i],d=t[i+1]||p,u=p[0]+c*(d[0]-p[0]),k=p[1],x=d[1]-k;x>180&&(x-=360),x<-180&&(x+=360);let P=k+c*x,b=at(p[0],p[1],d[0],d[1]);return{point:[u,P],bearing:b}}function lt(t,e,o,n=1500,l=[],i=[0,.05,.95,1],a="Ocean",r=null){if(m&&(cancelAnimationFrame(m),m=null),!t||!e||e.length===0)return;let c=V(e),p=typeof t._currentProgress=="number"?t._currentProgress:0,d=Math.max(0,Math.min(1,o)),u=performance.now(),k=i&&i.length>1?i[1]:.05,v=i&&i.length>2?i[2]:.95;function x(P){let b=P-u,g=n<=0?1:Math.min(1,b/n),D=1-Math.pow(1-g,3),C=p+(d-p)*D,{point:E,bearing:Z}=W(e,c,C);t.setLatLng(E);let _="Road",T="Ch\u1EB7ng 1: V\u1EADn chuy\u1EC3n \u0111\u01B0\u1EDDng b\u1ED9 (First-mile Road)",S="#FF9500",z=Math.abs(C-v)<=.015||C>=v&&Math.abs(d-v)<=.02;if(C<=k)_="Road",T="Ch\u1EB7ng 1: Xe t\u1EA3i container v\u1EADn chuy\u1EC3n ra C\u1EA3ng/S\xE2n bay xu\u1EA5t ph\xE1t",S="#FF9500";else if(z){_=a;let f=r&&r.arrival_hub&&r.arrival_hub.name?r.arrival_hub.name:"C\u1EA3ng/S\xE2n bay \u0111\u1EBFn";T="\u0110\xE3 c\u1EADp b\u1EBFn v\xE0 \u0111ang l\xE0m th\u1EE7 t\u1EE5c th\xF4ng quan h\u1EA3i quan t\u1EA1i "+f,S="#28a745"}else if(C<v)_=a,T=a==="Air"?"Ch\u1EB7ng 2: M\xE1y bay v\u1EADn t\u1EA3i \u0111ang bay qua kh\xF4ng ph\u1EADn Qu\u1ED1c t\u1EBF (Air Transit)":"Ch\u1EB7ng 2: T\xE0u container \u0111ang v\u01B0\u1EE3t h\u1EA3i tr\xECnh Th\xE1i B\xECnh D\u01B0\u01A1ng (Ocean Transit)",S=a==="Air"?"#007AFF":"#0055B3";else{_="Road";let f=r&&r.destination&&r.destination.name?r.destination.name:"Kho \u0111\xEDch nh\u1EADn h\xE0ng";T="Ch\u1EB7ng 3: Xe t\u1EA3i container giao nh\u1EADn v\u1EC1 "+f+" (Last-mile Road)",S="#FF9500"}let M=t.getElement?t.getElement():null;if(M){if(t._activeMode!==_){t._activeMode=_;let O=M.querySelector(".lw-vehicle-box");O&&(O.style.borderColor=S);let A=M.querySelector(".lw-vehicle-icon-svg");A&&(A.innerHTML=tt(_))}let f=M.querySelector(".lw-vehicle-icon-svg")||M.querySelector("svg");f&&(f.style.transform=`rotate(${Z}deg)`,f.style.transformOrigin="center center")}if(t._currentProgress=C,g<1)m=requestAnimationFrame(x);else{if(m=null,d<=.001)t.setLatLng(e[0]);else if(Math.abs(d-v)<=.02){let f=r&&r._ahCoord?r._ahCoord:null;!f&&r&&r.arrival_hub&&r.arrival_hub.coordinates&&(f=[r.arrival_hub.coordinates[0],X(r.arrival_hub.coordinates[1],e[e.length-1][1])]),f&&t.setLatLng([f[0],f[1]])}else d>=.999&&t.setLatLng(e[e.length-1]);if(t.getPopup&&t.getPopup()){let f=_==="Ocean"?"T\xE0u bi\u1EC3n \u{1F6A2}":_==="Air"?"M\xE1y bay \u2708\uFE0F":"Xe t\u1EA3i Container \u{1F69A}";t.setPopupContent(`<b>Ph\u01B0\u01A1ng ti\u1EC7n: ${f}</b><br>${T}<br><small>Ti\u1EBFn tr\xECnh to\xE0n tr\xECnh: ${(d*100).toFixed(1)}%</small>`)}}}m=requestAnimationFrame(x)}function X(t,e){if(typeof t!="number"||typeof e!="number")return t;let o=t;for(;o-e>180;)o-=360;for(;o-e<-180;)o+=360;return o}function ft(t,e,o){let n=window.L||window.leaflet;if(!n){$("#lw-map-info-text").html('<span style="color: red;">Th\u01B0 vi\u1EC7n b\u1EA3n \u0111\u1ED3 (Leaflet) ch\u01B0a \u0111\u01B0\u1EE3c t\u1EA3i.</span>');return}if(m&&(cancelAnimationFrame(m),m=null),s){try{s.remove()}catch(h){}s=null,y=null}L=[],J=null,s=n.map("shipment-map",{zoomControl:!0,attributionControl:!0}).setView([20,150],3),window._lw_shipment_map=s,s.on("popupopen",function(h){h&&h.popup&&h.popup._container&&$(h.popup._container).find(".leaflet-popup-close-button").each(function(){$(this).attr("href","javascript:void(0);").attr("role","button").on("click",function(w){return w.preventDefault(),w.stopPropagation(),w.stopImmediatePropagation(),s&&s.closePopup(),!1})})}),n.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',subdomains:["a","b","c"],maxZoom:19}).addTo(s),ot(t.method);let l=t.full_route&&t.full_route.length>0?t.full_route:t.route||[];if(!l||l.length===0){$("#lw-map-info-text").html('<span class="text-muted">Ch\u01B0a c\xF3 t\u1ECDa \u0111\u1ED9 n\xE0o \u0111\u01B0\u1EE3c ghi nh\u1EADn cho \u0111\u01A1n h\xE0ng n\xE0y.</span>');return}let i=I(l,.002);(!i||i.length<2)&&(i=l);let a=[];if(t.legs&&Array.isArray(t.legs)&&t.legs.length>0&&t.legs.forEach(h=>{let w=h.coordinates_latlon||[];if(w.length>=2){let F=I(w,.002);(!F||F.length<2)&&(F=w);let U=h.mode==="Road",xt=h.mode==="Air",bt=U?"#FF9500":xt?"#007AFF":"#0055B3",wt=U?"6, 8":"",yt=U?3.5:4,vt=n.polyline(F,{color:bt,weight:yt,opacity:.92,dashArray:wt}).addTo(s);a.push(vt)}}),a.length===0){let h=n.polyline(i,{color:t.method==="Air"?"#007AFF":t.method==="Ocean"?"#0055B3":"#FF9500",weight:3.5,opacity:.9,dashArray:t.method==="Road"?"6, 8":""}).addTo(s);a.push(h)}try{let h=n.featureGroup(a);s.fitBounds(h.getBounds(),{padding:[40,40],maxZoom:8})}catch(h){}let r=i[0],c=t.origin&&t.origin.name||(typeof t.origin=="string"?t.origin:"Kho nh\xE0 m\xE1y xu\u1EA5t ph\xE1t"),p=n.divIcon({className:"custom-origin-icon",html:'<div style="background: #28a745; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.35); cursor: pointer;" title="\u0110i\u1EC3m xu\u1EA5t ph\xE1t (Origin - \u0110i\u1EC3m O)">O</div>',iconSize:[28,28],iconAnchor:[14,14]}),d=n.marker(r,{icon:p}).addTo(s);d.bindPopup(`<b>Kho xu\u1EA5t ph\xE1t (Origin - \u0110i\u1EC3m O):</b><br>${c}<br><small>To\u1EA1 \u0111\u1ED9: ${r[0].toFixed(4)}, ${r[1].toFixed(4)}</small>`),L.push(d);let u=i[i.length-1],k=t.destination&&t.destination.name||(typeof t.destination=="string"?t.destination:"Kho \u0111\xEDch nh\u1EADn h\xE0ng"),v=n.divIcon({className:"custom-dest-icon",html:'<div style="background: #dc3545; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.35); cursor: pointer;" title="\u0110i\u1EC3m \u0111\xEDch \u0111\u1EBFn (Destination - \u0110i\u1EC3m D)">D</div>',iconSize:[28,28],iconAnchor:[14,14]}),x=n.marker(u,{icon:v}).addTo(s),P=((u[1]+180)%360+360)%360-180;x.bindPopup(`<b>Kho \u0111\xEDch nh\u1EADn h\xE0ng (Destination - \u0110i\u1EC3m D):</b><br>${k}<br><small>To\u1EA1 \u0111\u1ED9: ${u[0].toFixed(4)}, ${P.toFixed(4)}</small>`),L.push(x);let b=null;if(t.legs&&t.legs.length>=1&&t.legs[0].coordinates_latlon&&t.legs[0].coordinates_latlon.length>0){let h=t.legs[0].coordinates_latlon;b=h[h.length-1]}else t.departure_hub&&t.departure_hub.coordinates&&(b=[t.departure_hub.coordinates[0],X(t.departure_hub.coordinates[1],r[1])]);if(b&&t.departure_hub){let h=n.divIcon({className:"custom-dep-hub-icon",html:`<div style="background: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: 2.5px solid ${t.method==="Air"?"#007AFF":"#0055B3"}; box-shadow: 0 2px 6px rgba(0,0,0,0.25); cursor: pointer;" title="Tr\u1EA1m trung chuy\u1EC3n xu\u1EA5t ph\xE1t">
                    ${et(t.method)}
                </div>`,iconSize:[30,30],iconAnchor:[15,15]}),w=n.marker([b[0],b[1]],{icon:h}).addTo(s),F=((b[1]+180)%360+360)%360-180;w.bindPopup(`<b>Tr\u1EA1m trung chuy\u1EC3n xu\u1EA5t ph\xE1t:</b><br>${t.departure_hub.name||"C\u1EA3ng/S\xE2n bay xu\u1EA5t"}<br><small>To\u1EA1 \u0111\u1ED9: ${b[0].toFixed(4)}, ${F.toFixed(4)}</small>`),L.push(w)}let g=null;if(t.legs&&t.legs.length>=2&&t.legs[1].coordinates_latlon&&t.legs[1].coordinates_latlon.length>0){let h=t.legs[1].coordinates_latlon;g=h[h.length-1]}else t.arrival_hub&&t.arrival_hub.coordinates&&(g=[t.arrival_hub.coordinates[0],X(t.arrival_hub.coordinates[1],u[1])]);if(g&&t.arrival_hub){let h=n.divIcon({className:"custom-arr-hub-icon",html:`<div style="background: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: 2.5px solid ${t.method==="Air"?"#007AFF":"#0055B3"}; box-shadow: 0 2px 6px rgba(0,0,0,0.25); cursor: pointer;" title="Tr\u1EA1m trung chuy\u1EC3n \u0111\u1EBFn">
                    ${et(t.method)}
                </div>`,iconSize:[30,30],iconAnchor:[15,15]}),w=n.marker([g[0],g[1]],{icon:h}).addTo(s),F=((g[1]+180)%360+360)%360-180;w.bindPopup(`<b>Tr\u1EA1m trung chuy\u1EC3n \u0111\u1EBFn:</b><br>${t.arrival_hub.name||"C\u1EA3ng/S\xE2n bay \u0111\u1EBFn"}<br><small>To\u1EA1 \u0111\u1ED9: ${g[0].toFixed(4)}, ${F.toFixed(4)}</small>`),L.push(w)}t._dhCoord=b,t._ahCoord=g;let D=typeof t.progress=="number"?t.progress:.55,C=t.progress_thresholds||[0,.05,.95,1],E="Road";D>C[1]&&D<=C[2]&&(E=t.method);let Z=E==="Road"?"#FF9500":t.method==="Air"?"#007AFF":"#0055B3",_=V(i),T=W(i,_,0),S=n.divIcon({className:"custom-vehicle-icon",html:`
                <div class="lw-vehicle-box" style="background: white; border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.3); border: 2.8px solid ${Z}; transition: border-color 0.3s;">
                    <div class="lw-vehicle-icon-svg" style="display: flex; align-items: center; justify-content: center; transform: rotate(${T.bearing}deg); transform-origin: center center;">
                        ${tt(E)}
                    </div>
                </div>
            `,iconSize:[42,42],iconAnchor:[21,21]}),z=n.marker(T.point,{icon:S,zIndexOffset:1e3}).addTo(s);z._currentProgress=0,z._activeMode=E,z.bindPopup(`<b>V\u1ECB tr\xED ph\u01B0\u01A1ng ti\u1EC7n:</b><br>${t.current_location||"\u0110ang v\u1EADn chuy\u1EC3n"}`),L.push(z),lt(z,i,D,1600,t.legs||[],C,t.method,t),setTimeout(()=>{z&&s&&s.hasLayer(z)&&z.openPopup()},1650);let M=t.method==="Air"?"\u2708\uFE0F \u0110a ph\u01B0\u01A1ng th\u1EE9c H\xE0ng kh\xF4ng (Air)":t.method==="Ocean"?"\u{1F6A2} \u0110a ph\u01B0\u01A1ng th\u1EE9c \u0110\u01B0\u1EDDng bi\u1EC3n (Ocean)":"\u{1F69A} \u0110\u01B0\u1EDDng b\u1ED9 n\u1ED9i \u0111\u1ECBa (Road)",f="#e0f2fe",O="#0369a1",A="\u{1F6A2}";t.progress>=1||t.status_text&&(t.status_text.includes("giao h\xE0ng th\xE0nh c\xF4ng")||t.status_text.includes("Ho\xE0n th\xE0nh"))?(f="#dcfce7",O="#15803d",A="\u2705"):t.status_text&&(t.status_text.includes("th\xF4ng quan")||t.status_text.includes("H\u1EA3i quan")||t.status_text.includes("Customs"))?(f="#fef3c7",O="#b45309",A="\u{1F3DB}\uFE0F"):t.method==="Air"&&(A="\u2708\uFE0F");let mt=`
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <!-- T\u1EA7ng 1: Banner Tr\u1EA1ng th\xE1i v\u1EADn h\xE0nh -->
                <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 7px 12px; border-radius: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; color: #64748b;">Tr\u1EA1ng th\xE1i v\u1EADn h\xE0nh</span>
                    <span class="badge" style="background: ${f}; color: ${O}; font-size: 11.5px; font-weight: 600; padding: 4px 10px; border-radius: 10px; white-space: normal; text-align: right; line-height: 1.3; max-width: 72%;">
                        ${A} ${t.status_text}
                    </span>
                </div>

                <!-- T\u1EA7ng 2: 2 Kh\u1ED1i 50-50 C\xE2n x\u1EE9ng -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div style="background: #ffffff; padding: 9px 12px; border-radius: 6px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div>
                            <div style="font-size: 10.5px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 2px;">M\xF4 h\xECnh v\u1EADn t\u1EA3i</div>
                            <div style="font-size: 12px; font-weight: 600; color: #0f172a; line-height: 1.3;">${M}</div>
                        </div>
                        <div style="font-size: 11.5px; color: #0284c7; font-weight: 600; margin-top: 4px;">
                            C\u1EF1 ly: ${Math.round(t.distance_km||0).toLocaleString()} km
                        </div>
                    </div>

                    <div style="background: #ffffff; padding: 9px 12px; border-radius: 6px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div>
                            <div style="font-size: 10.5px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 2px;">V\u1ECB tr\xED hi\u1EC7n t\u1EA1i</div>
                            <div style="font-size: 12px; font-weight: 600; color: #0284c7; line-height: 1.3; word-break: break-word;" title="${t.current_location}">
                                \u{1F4CD} ${t.current_location}
                            </div>
                        </div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                            Ti\u1EBFn tr\xECnh: <strong style="color: #0284c7;">${Math.round((t.progress||0)*100)}%</strong>
                        </div>
                    </div>
                </div>
            </div>
        `;$("#lw-map-info-text").html(mt),gt(e,o,t),setTimeout(()=>{s&&s.invalidateSize()},300)}function gt(t,e,o){let n=$("#lw-timeline-container");if(o&&o.checkpoints&&o.checkpoints.length>0){H(o.checkpoints,n,o);return}if(window.cur_frm&&cur_frm.doc&&cur_frm.doc.name===t&&cur_frm.doc.transit_route&&cur_frm.doc.transit_route.length>0){H(cur_frm.doc.transit_route,n,o);return}let l=e,i=t;e==="Purchase Order"?frappe.db.get_value("Shipment Tracking",{purchase_order:t},"name").then(a=>{a&&a.message&&a.message.name?frappe.db.get_doc("Shipment Tracking",a.message.name).then(r=>{H(r.transit_route||[],n,o)}):n.html('<div style="color: #8d99a6; font-size: 12px; padding: 8px 0;">Ch\u01B0a li\xEAn k\u1EBFt phi\u1EBFu Shipment Tracking ho\u1EB7c ch\u01B0a c\xF3 l\u1ED9 tr\xECnh chi ti\u1EBFt.</div>')}):e==="Shipment Tracking"?frappe.db.get_doc("Shipment Tracking",t).then(a=>{H(a.transit_route||[],n,o)}):n.html('<div style="color: #8d99a6; font-size: 12px; padding: 8px 0;">Kh\xF4ng c\xF3 d\u1EEF li\u1EC7u l\u1ED9 tr\xECnh.</div>')}function H(t,e,o){if(!t||t.length===0){e.html('<div style="color: #8d99a6; font-size: 12px; padding: 8px 0;">Ch\u01B0a c\xF3 tr\u1EA1m l\u1ED9 tr\xECnh n\xE0o.</div>');return}let n=t.some(i=>i.is_current===!0||i.activity&&i.activity.includes("(Current Position)")),l='<div class="lw-timeline">';t.forEach((i,a)=>{let r=a===t.length-1,c=i.is_current===!0||i.activity&&i.activity.includes("(Current Position)")||!n&&r,p=(i.activity||"").replace(" (Current Position)","").replace("(Current Position)","").trim(),d=c?"lw-timeline-item current-step":"lw-timeline-item completed",u=c?'<span class="lw-timeline-current-badge">\u{1F4CD} V\u1ECB tr\xED hi\u1EC7n t\u1EA1i</span>':"";l+=`
                <div class="${d}">
                    <div class="lw-timeline-node"></div>
                    <div class="lw-timeline-date">${i.date||""}</div>
                    <div class="lw-timeline-title">
                        <span>${p}</span>
                        ${u}
                    </div>
                    <div class="lw-timeline-desc">\u{1F4CD} ${i.location||""}</div>
                    ${i.notes?`<div class="lw-timeline-notes">${i.notes}</div>`:""}
                </div>
            `}),l+="</div>",e.html(l)}function Y(t,e=!1){if((!t||t!=="import"&&t!=="export")&&(t="import"),B=t,t==="export"?($("#lw-tab-export").addClass("active").css({background:"#ffffff",color:"#0071E3","font-weight":"600","box-shadow":"0 1px 3px rgba(0,0,0,0.08)"}),$("#lw-tab-import").removeClass("active").css({background:"transparent",color:"#495057","font-weight":"500","box-shadow":"none"}),$("#lw-import-step-list").hide(),$("#lw-export-step-list").show()):($("#lw-tab-import").addClass("active").css({background:"#ffffff",color:"#0071E3","font-weight":"600","box-shadow":"0 1px 3px rgba(0,0,0,0.08)"}),$("#lw-tab-export").removeClass("active").css({background:"transparent",color:"#495057","font-weight":"500","box-shadow":"none"}),$("#lw-export-step-list").hide(),$("#lw-import-step-list").show()),e){let o=typeof frappe!="undefined"&&frappe.get_route?frappe.get_route():[];o&&o[0]==="Form"&&o[1]&&o[2]&&frappe.call({method:"logistics_wizard.api.get_workflow_chain_status",args:{doctype:o[1],docname:o[2],flow_type:B},callback:function(n){n&&n.message&&n.message.success&&st(n.message.steps,B)}})}}function G(){[...R,...N].forEach(e=>{let o=$("#"+e.id);if(o.length){o.removeClass("wiz-step-completed wiz-step-current wiz-step-pending"),o.find(".wiz-check-badge").html("");let n=o.find("a");n.attr("href","/app/"+e.slug),n.text(e.label)}})}function st(t,e){if(!t||!t.length)return;let n=(e||B)==="export"?N:R;t.forEach((l,i)=>{let a=n[i];if(!a)return;let r=$("#"+a.id);if(!r.length)return;let c=l.label||a.label,p=l.url||"/app/"+a.slug,d=r.find("a");d.attr("href",p),d.text(c),l.completed?(r.addClass("wiz-step-completed"),r.find(".wiz-check-badge").html("\u2714")):l.is_current?r.addClass("wiz-step-current"):r.addClass("wiz-step-pending"),l.is_current&&r.addClass("wiz-step-current")})}function pt(){if(j(),typeof frappe=="undefined"||!frappe.get_route)return;let t=frappe.get_route();if(!(!t||!t.length))if(t[0]==="Form"&&t[1]&&K.includes(t[1])&&t[2]){let e=t[1],o=t[2],n=null;q.includes(e)?n="export":Q.includes(e)&&(n="import"),frappe.call({method:"logistics_wizard.api.get_workflow_chain_status",args:{doctype:e,docname:o,flow_type:n},callback:function(l){if(G(),l&&l.message&&l.message.success){let i=l.message.flow_type||n||"import";Y(i,!1),st(l.message.steps,i)}}})}else if(t[0]==="List"&&t[1]&&K.includes(t[1])){G();let e=t[1],o=q.includes(e)?"export":"import";Y(o,!1);let n=(o==="export"?"wiz-exp-":"wiz-")+e.replace(/\s+/g,"-");$("#"+n).addClass("wiz-step-current")}else G()}typeof frappe!="undefined"&&frappe.router&&frappe.router.on("change",function(){let t=typeof frappe.get_route=="function"?frappe.get_route():[];if(t&&t[0]==="shipment-tracking-hub"){frappe.route_options=Object.assign({},frappe.route_options,{tab:"tracking"}),frappe.set_route("managementLogistic");return}else if(t&&t[0]==="trade-case-overview"){frappe.route_options=Object.assign({},frappe.route_options,{tab:"overview"}),frappe.set_route("managementLogistic");return}j(),pt()}),window.LogisticsWizardMap={douglasPeucker:I,perpendicularDistance:rt,calculateBearing:at,computePolylineMetrics:V,interpolateAtProgress:W,animateVehicle:lt,update_marine_overlay:ot,getShipmentMap:function(){return s},getSeaOverlayLayer:function(){return y},getMapPolyline:function(){return J},getMapMarkers:function(){return L}},j(),setTimeout(pt,300),setTimeout(j,1e3)}document.readyState==="loading"?$(document).ready(ct):ct();})();
//# sourceMappingURL=smart_workflow_widget.bundle.WAIXQELG.js.map
