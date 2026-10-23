(()=>{console.log("SMART WORKFLOW WIDGET SCRIPT LOADED");function de(){let R=[{doctype:"Material Request",id:"wiz-Material-Request",slug:"material-request",label:"1. Y\xEAu c\u1EA7u mua h\xE0ng (Material Request)"},{doctype:"Purchase Order",id:"wiz-Purchase-Order",slug:"purchase-order",label:"2. \u0110\u01A1n \u0111\u1EB7t h\xE0ng (Purchase Order)"},{doctype:"Payment Entry",id:"wiz-Payment-Entry",slug:"payment-entry",label:"3. \u0110\u1EB7t c\u1ECDc / T\u1EA1m \u1EE9ng (Payment Entry)"},{doctype:"Shipment Tracking",id:"wiz-Shipment-Tracking",slug:"shipment-tracking-hub",label:"4. Theo d\xF5i h\xE0nh tr\xECnh (Shipment Tracking)"},{doctype:"Purchase Receipt",id:"wiz-Purchase-Receipt",slug:"purchase-receipt",label:"5. Nh\u1EADn h\xE0ng (Purchase Receipt)"},{doctype:"Landed Cost Voucher",id:"wiz-Landed-Cost-Voucher",slug:"landed-cost-voucher",label:"6. Ph\xE2n b\u1ED5 gi\xE1 v\u1ED1n (Landed Cost)"},{doctype:"Stock Entry",id:"wiz-Stock-Entry",slug:"stock-entry",label:"7. Nh\u1EADp kho (Stock Entry)"}],j=[{doctype:"Sales Order",id:"wiz-exp-Sales-Order",slug:"sales-order",label:"1. \u0110\u01A1n b\xE1n h\xE0ng (Sales Order)"},{doctype:"Payment Entry",id:"wiz-exp-Payment-Entry-Deposit",slug:"payment-entry",label:"2. Thu ti\u1EC1n c\u1ECDc (Payment Entry)"},{doctype:"Stock Entry",id:"wiz-exp-Stock-Entry",slug:"stock-entry",label:"3. Chuy\u1EC3n kho c\u1EA3ng (Stock Entry)"},{doctype:"Delivery Note",id:"wiz-exp-Delivery-Note",slug:"delivery-note",label:"4. Xu\u1EA5t kho giao h\xE0ng (Delivery Note)"},{doctype:"Shipment Tracking",id:"wiz-exp-Shipment-Tracking",slug:"shipment-tracking-hub",label:"5. Theo d\xF5i h\xE0nh tr\xECnh (Shipment Tracking)"},{doctype:"Sales Invoice",id:"wiz-exp-Sales-Invoice",slug:"sales-invoice",label:"6. H\xF3a \u0111\u01A1n th\u01B0\u01A1ng m\u1EA1i (Sales Invoice)"},{doctype:"Payment Entry",id:"wiz-exp-Payment-Entry-Final",slug:"payment-entry",label:"7. T\u1EA5t to\xE1n ngo\u1EA1i t\u1EC7 (Payment Entry)"}],_e=R,U=["Material Request","Purchase Order","Purchase Receipt","Landed Cost Voucher"],q=["Sales Order","Delivery Note","Sales Invoice"],he=["Payment Entry","Shipment Tracking","Stock Entry"],K=Array.from(new Set([...U,...q,...he])),ke=K,B="import",a=null,J=null,z=[],y=null,m=null;$(document).on("click",".leaflet-popup-close-button",function(e){return e.preventDefault(),e.stopPropagation(),e.stopImmediatePropagation(),a&&a.closePopup(),!1});function ee(e){return e==="Air"?`
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#007AFF" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1.5C11.2 1.5 10.6 2.3 10.6 3.2V8.8L2.4 13.5C1.8 13.8 1.5 14.5 1.5 15.1C1.5 15.9 2.2 16.5 3 16.5H10.6V20.2L8.2 21.8C7.9 22 7.7 22.3 7.7 22.7C7.7 23.4 8.3 24 9 24H15C15.7 24 16.3 23.4 16.3 22.7C16.3 22.3 16.1 22 15.8 21.8L13.4 20.2V16.5H21C21.8 16.5 22.5 15.9 22.5 15.1C22.5 14.5 22.2 13.8 21.6 13.5L13.4 8.8V3.2C13.4 2.3 12.8 1.5 12 1.5Z" stroke="#0047AB" stroke-width="0.5"/>
                </svg>
            `:e==="Ocean"?`
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
            `}function te(e){return e==="Ocean"||e==="seaport"||e==="port"?`
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#0055B3" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="5" r="3"/>
                    <line x1="12" y1="22" x2="12" y2="8"/>
                    <path d="M5 12H2a10 10 0 0 0 20 0h-3"/>
                </svg>
            `:`
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#007AFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.2-1.1.6L2.5 8l6.4 3.3L7 15l-3.3-1.1-1.2 1.3 4.2 3.8 3.8 4.2 1.3-1.2L10.7 18.7l3.7-1.9 3.3 6.4 1.2-1.2-.4-2.6Z"/>
                </svg>
            `}function N(){if($("#lw-fab-container").length===0){let e=`
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
                        <button class="lw-fab lw-sub-fab" id="lw-fab-workflow" data-tooltip="Ti\u1EBFn tr\xECnh (Workflow)">\u{1F4CB}</button>
                        <button class="lw-fab lw-sub-fab" id="lw-fab-shipment" data-tooltip="H\xE0nh tr\xECnh (Shipment)">\u{1F69A}</button>
                        <button class="lw-fab lw-sub-fab" id="lw-fab-ai" data-tooltip="AI Chat">\u{1F916}</button>
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
                            \u{1F4E5} Nh\u1EADp Kh\u1EA9u
                        </button>
                        <button type="button" class="lw-tab-btn" id="lw-tab-export" data-flow="export" style="flex: 1; border: none; outline: none; background: transparent; color: #495057; font-weight: 500; font-size: 12px; padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: all 0.2s;">
                            \u{1F4E4} Xu\u1EA5t Kh\u1EA9u
                        </button>
                    </div>
                    <div class="lw-popup-body" style="padding: 10px 14px 14px 14px;">
                        <!-- Danh s\xE1ch Nh\u1EADp kh\u1EA9u -->
                        <ul class="lw-step-list" id="lw-import-step-list">
                            ${R.map(t=>`
                                <li class="lw-step-item" id="${t.id}">
                                    <span class="wiz-check-badge"></span>
                                    <a href="/app/${t.slug}">${t.label}</a>
                                </li>
                            `).join("")}
                        </ul>
                        <!-- Danh s\xE1ch Xu\u1EA5t kh\u1EA9u -->
                        <ul class="lw-step-list" id="lw-export-step-list" style="display: none;">
                            ${j.map(t=>`
                                <li class="lw-step-item" id="${t.id}">
                                    <span class="wiz-check-badge"></span>
                                    <a href="/app/${t.slug}">${t.label}</a>
                                </li>
                            `).join("")}
                        </ul>
                    </div>
                </div>

                <!-- Popup: Shipment (Map & Timeline) -->
                <div class="lw-popup lw-popup-large" id="lw-popup-shipment">
                    <div class="lw-popup-header" style="display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; gap: 8px;">
                        <span style="font-weight: 600; font-size: 13px;">\u{1F5FA}\uFE0F B\u1EA3n \u0111\u1ED3 & H\xE0nh tr\xECnh V\u1EADn chuy\u1EC3n To\xE0n c\u1EA7u</span>
                        <div style="display: flex; align-items: center; gap: 8px; margin-left: auto;">
                            <button id="lw-btn-open-full-hub" class="btn btn-xs" style="background: #0071E3; color: #ffffff; border: none; border-radius: 5px; font-size: 11px; font-weight: 600; padding: 3px 9px; cursor: pointer; display: inline-flex; align-items: center; gap: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.15);" title="M\u1EDF trang Qu\u1EA3n tr\u1ECB V\u1EADn chuy\u1EC3n Chuy\xEAn s\xE2u">
                                <span>M\u1EDF to\xE0n trang Qu\u1EA3n tr\u1ECB Hub</span> \u2197
                            </button>
                            <span class="lw-popup-close" data-target="#lw-popup-shipment" style="cursor: pointer; font-size: 13px; padding: 2px 4px;">\u2716</span>
                        </div>
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
                        <div style="font-size: 44px; margin-bottom: 12px;">\u{1F916}</div>
                        <h4 style="margin:0 0 10px 0; color: #1f272e;">Tr\u1EE3 l\xFD RAG H\u1EA3i quan</h4>
                        <p style="color: #6c757d; font-size: 13px; line-height: 1.5; margin: 0;">
                            H\u1EC7 th\u1ED1ng AI RAG h\u1ED7 tr\u1EE3 tra c\u1EE9u v\u0103n b\u1EA3n ph\xE1p lu\u1EADt H\u1EA3i quan v\xE0 \u0111\u1EC1 xu\u1EA5t m\xE3 HS Code \u0111ang k\u1EBFt n\u1ED1i!
                        </p>
                    </div>
                </div>
            `;$("body").append(e),$("#lw-fab-main").on("click",function(){$(this).toggleClass("active"),$(this).hasClass("active")?$("#lw-fab-menu").addClass("show"):($("#lw-fab-menu").removeClass("show"),$(".lw-popup").hide())}),$(".lw-sub-fab").on("click",function(t){let o=$(this).attr("id"),n=o.replace("lw-fab-","lw-popup-");$(".lw-popup").hide(),$("#"+n).show(),o==="lw-fab-shipment"&&ue()}),$(document).on("click","#lw-btn-open-full-hub",function(t){t.preventDefault(),$(".lw-popup").hide(),$("#lw-fab-menu").removeClass("show"),$("#lw-fab-main").removeClass("active");let o=typeof frappe!="undefined"&&frappe.get_route?frappe.get_route():[],n={};o&&o[0]==="Form"&&["Purchase Order","Shipment Tracking","Purchase Receipt"].includes(o[1])&&o[2]&&(n={shipment:o[2],doctype:o[1]}),typeof frappe!="undefined"&&frappe.set_route?frappe.set_route("shipment-tracking-hub",n):window.location.href="/app/shipment-tracking-hub"+(n.shipment?"?shipment="+encodeURIComponent(n.shipment):"")}),$(document).on("click","#wiz-Shipment-Tracking a, #wiz-exp-Shipment-Tracking a",function(t){typeof frappe!="undefined"&&frappe.set_route&&(t.preventDefault(),$(".lw-popup").hide(),$("#lw-fab-menu").removeClass("show"),$("#lw-fab-main").removeClass("active"),frappe.set_route("shipment-tracking-hub"))}),$(document).on("click",".lw-tab-btn",function(t){t.preventDefault();let o=$(this).data("flow");G(o,!0)}),$(".lw-popup-close").on("click",function(){if($($(this).data("target")).hide(),m&&(cancelAnimationFrame(m),m=null),a){try{a.remove()}catch(t){}a=null,y=null}})}}function ue(){let e=typeof frappe!="undefined"&&frappe.get_route?frappe.get_route():[];e&&e[0]==="Form"&&e[1]&&["Purchase Order","Shipment Tracking","Purchase Receipt"].includes(e[1])&&e[2]?oe(e[2],e[1]):ie()}function ie(e="active"){let t=$("#lw-shipment-content"),o=`
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 8px;">
                <div style="flex: 1; min-width: 0;">
                    <strong style="color: #1f272e; font-size: 13.5px;">Danh s\xE1ch L\xF4 h\xE0ng Qu\u1ED1c t\u1EBF:</strong>
                    <div style="font-size: 11px; color: #6c757d; margin-top: 2px;">Nh\u1EA5n v\xE0o \u0111\u01A1n h\xE0ng \u0111\u1EC3 xem b\u1EA3n \u0111\u1ED3 l\u1ED9 tr\xECnh tr\u1EF1c ti\u1EBFp:</div>
                </div>
                <div style="flex-shrink: 0;">
                    <select id="lw-filter-status" class="form-control" style="font-size: 11.5px; height: 28px; border-radius: 6px; border: 1px solid #ced4da; background-color: #ffffff; padding: 1px 6px; cursor: pointer; min-width: 145px; font-weight: 500; color: #1f272e; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                        <option value="active" ${e==="active"?"selected":""}>\u{1F69A} \u0110ang v\u1EADn chuy\u1EC3n</option>
                        <option value="completed" ${e==="completed"?"selected":""}>\u2705 \u0110\xE3 ho\xE0n th\xE0nh</option>
                        <option value="customs" ${e==="customs"?"selected":""}>\u{1F3DB}\uFE0F \u0110ang th\xF4ng quan</option>
                        <option value="all" ${e==="all"?"selected":""}>\u{1F310} T\u1EA5t c\u1EA3 \u0111\u01A1n h\xE0ng</option>
                    </select>
                </div>
            </div>
            <div id="lw-shipment-items-container">
                <div style="text-align: center; padding: 25px; color: #6c757d;">
                    <div class="spinner-border text-primary" role="status" style="width: 1.8rem; height: 1.8rem;"></div>
                    <div style="margin-top: 8px; font-size: 12px;">\u0110ang t\u1EA3i danh s\xE1ch l\xF4 h\xE0ng...</div>
                </div>
            </div>
        `;t.html(o),$("#lw-filter-status").on("change",function(){let n=$(this).val();ne(n)}),ne(e)}function ne(e){let t=$("#lw-shipment-items-container");t.html(`
            <div style="text-align: center; padding: 25px; color: #6c757d;">
                <div class="spinner-border text-primary" role="status" style="width: 1.8rem; height: 1.8rem;"></div>
                <div style="margin-top: 8px; font-size: 12px;">\u0110ang l\u1ECDc danh s\xE1ch \u0111\u01A1n h\xE0ng...</div>
            </div>
        `),frappe.call({method:"logistics_wizard.api.get_active_shipments",args:{status_filter:e},callback:function(o){if(o.message&&o.message.status==="success"){let n=o.message.data||[];if(n.length===0){let i=e==="active"?"\u0111ang v\u1EADn chuy\u1EC3n":e==="completed"?"\u0111\xE3 ho\xE0n th\xE0nh":e==="customs"?"\u0111ang l\xE0m th\u1EE7 t\u1EE5c th\xF4ng quan":"";t.html(`
                            <div style="text-align: center; padding: 35px 20px; color: #8d99a6;">
                                <div style="font-size: 32px; margin-bottom: 8px;">\u{1F4E6}</div>
                                <strong>Kh\xF4ng c\xF3 \u0111\u01A1n h\xE0ng n\xE0o ${i}.</strong>
                                <p style="font-size: 12px; margin-top: 6px;">H\xE3y th\u1EED ch\u1ECDn b\u1ED9 l\u1ECDc kh\xE1c (v\xED d\u1EE5 "To\xE0n b\u1ED9 \u0111\u01A1n h\xE0ng") \u0111\u1EC3 xem t\u1EA5t c\u1EA3.</p>
                            </div>
                        `);return}let r='<div class="lw-shipment-list" style="display: flex; flex-direction: column; gap: 8px;">';n.forEach(i=>{let s="#e7f1ff",l="#007AFF",p="\u{1F69A}";i.is_completed||i.status==="Completed"?(s="#e6f4ea",l="#137333",p="\u2705"):i.is_customs||i.status==="Customs Clearance"?(s="#fef7e0",l="#b06000",p="\u{1F3DB}\uFE0F"):i.status==="Draft"&&(s="#f1f3f4",l="#5f6368",p="\u{1F4DD}");let c=i.shipping_method==="Air"?"\u2708\uFE0F":i.shipping_method==="Ocean"?"\u{1F6A2}":"\u{1F69A}",d=i.origin_port&&i.destination_port?` &bull; ${i.origin_port} \u2192 ${i.destination_port}`:"";r+=`
                            <div class="lw-shipment-item" data-name="${i.name}" style="padding: 12px 14px; background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; cursor: pointer; transition: all 0.2s;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong style="color: #007AFF; font-size: 13px;">${i.name}</strong>
                                        <span style="font-size: 11px; color: #6c757d; margin-left: 6px;">${c}${d}</span>
                                    </div>
                                    <span class="badge" style="background: ${s}; color: ${l}; font-weight: 500; font-size: 11px; padding: 4px 8px; border-radius: 4px;">
                                        ${p} ${i.status}
                                    </span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #495057; margin-top: 5px;">
                                    <div><strong>Nh\xE0 cung c\u1EA5p:</strong> ${i.supplier_name||"N/A"}</div>
                                    ${i.shipment_tracking?`<span style="color: #6c757d; font-size: 11px;">V\u1EADn \u0111\u01A1n: <strong>${i.shipment_tracking}</strong></span>`:""}
                                </div>
                            </div>
                        `}),r+="</div>",t.html(r),$(".lw-shipment-item").hover(function(){$(this).css({background:"#eef5ff","border-color":"#b8d5fd"})},function(){$(this).css({background:"#f8f9fa","border-color":"#e9ecef"})}).on("click",function(){let i=$(this).data("name");oe(i,"Purchase Order")})}else t.html('<div style="text-align: center; color: red; padding: 20px;">L\u1ED7i t\u1EA3i danh s\xE1ch v\u1EADn chuy\u1EC3n.</div>')}})}function oe(e,t){$("#lw-shipment-content").html(`
            <div class="lw-map-panel">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <button class="btn btn-xs btn-default" id="lw-btn-back-shipments">\u2190 Quay l\u1EA1i danh s\xE1ch</button>
                    <div style="text-align: right;">
                        <span style="font-size: 11px; color: #6c757d;">${t}:</span>
                        <strong style="color: #007AFF; font-size: 13px; margin-left: 4px;">${e}</strong>
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
        `),$("#lw-btn-back-shipments").on("click",function(){if(m&&(cancelAnimationFrame(m),m=null),a){try{a.remove()}catch(n){}a=null,y=null}ie()}),frappe.call({method:"logistics_wizard.api.get_shipment_tracking",args:{docname:e,doctype:t},callback:function(n){n.message&&n.message.status==="success"?fe(n.message.data,e,t):$("#lw-map-info-text").html(`<span style="color: #d9534f;">${n.message?n.message.message:"Kh\xF4ng th\u1EC3 t\u1EA3i th\xF4ng tin l\u1ED9 tr\xECnh."}</span>`)}})}function le(e){let t=window.L||window.leaflet;if(!t||!a)return;e==="Ocean"||e==="Sea"?(y||(y=t.tileLayer("https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",{attribution:'Map data: &copy; <a href="http://www.openseamap.org">OpenSeaMap</a> contributors',maxZoom:18,opacity:1})),a.hasLayer(y)||y.addTo(a)):y&&a.hasLayer(y)&&a.removeLayer(y)}function se(e,t,o){let[n,r]=e,[i,s]=t,[l,p]=o,c=p-s,d=l-i;c>180&&(c-=360),c<-180&&(c+=360);let u=r-s,k=n-i;u>180&&(u-=360),u<-180&&(u+=360);let v=c*c+d*d;if(v===0)return Math.hypot(u,k);let x=Math.max(0,Math.min(1,(u*c+k*d)/v)),S=x*c,b=x*d;return Math.hypot(u-S,k-b)}function D(e,t=.002){if(!e||!Array.isArray(e)||e.length<=2)return e||[];let o=0,n=0,r=e.length-1;for(let i=1;i<r;i++){let s=se(e[i],e[0],e[r]);s>o&&(o=s,n=i)}if(o>t){let i=D(e.slice(0,n+1),t),s=D(e.slice(n),t);return i.slice(0,i.length-1).concat(s)}else return[e[0],e[r]]}function re(e,t,o,n){let r=Math.PI/180,i=180/Math.PI,s=e*r,l=o*r,p=(n-t)*r;for(;p>Math.PI;)p-=2*Math.PI;for(;p<-Math.PI;)p+=2*Math.PI;let c=Math.sin(p)*Math.cos(l),d=Math.cos(s)*Math.sin(l)-Math.sin(s)*Math.cos(l)*Math.cos(p);return(Math.atan2(c,d)*i+360)%360}function V(e){let t=[0],o=0;if(!e||e.length<=1)return{cumulative:[0],total:0};for(let n=0;n<e.length-1;n++){let[r,i]=e[n],[s,l]=e[n+1],p=l-i;p>180&&(p-=360),p<-180&&(p+=360);let c=s-r,d=Math.cos((r+s)/2*Math.PI/180);o+=Math.hypot(c,p*d),t.push(o)}return{cumulative:t,total:o}}function W(e,t,o){if(!e||e.length===0)return{point:[0,0],bearing:0};if(e.length===1)return{point:e[0],bearing:0};let n=Math.max(0,Math.min(1,o));if(t.total===0)return{point:e[0],bearing:0};let r=n*t.total,i=0;for(let g=0;g<t.cumulative.length-1;g++)if(r>=t.cumulative[g]&&r<=t.cumulative[g+1]){i=g;break}i>=e.length-1&&(i=e.length-2);let s=t.cumulative[i],l=t.cumulative[i+1]-s,p=l===0?0:Math.max(0,Math.min(1,(r-s)/l)),c=e[i],d=e[i+1]||c,u=c[0]+p*(d[0]-c[0]),k=c[1],x=d[1]-k;x>180&&(x-=360),x<-180&&(x+=360);let S=k+p*x,b=re(c[0],c[1],d[0],d[1]);return{point:[u,S],bearing:b}}function ae(e,t,o,n=1500,r=[],i=[0,.05,.95,1],s="Ocean",l=null){if(m&&(cancelAnimationFrame(m),m=null),!e||!t||t.length===0)return;let p=V(t),c=typeof e._currentProgress=="number"?e._currentProgress:0,d=Math.max(0,Math.min(1,o)),u=performance.now(),k=i&&i.length>1?i[1]:.05,v=i&&i.length>2?i[2]:.95;function x(S){let b=S-u,g=n<=0?1:Math.min(1,b/n),I=1-Math.pow(1-g,3),C=c+(d-c)*I,{point:O,bearing:Z}=W(t,p,C);e.setLatLng(O);let _="Road",F="Ch\u1EB7ng 1: V\u1EADn chuy\u1EC3n \u0111\u01B0\u1EDDng b\u1ED9 (First-mile Road)",M="#FF9500",T=Math.abs(C-v)<=.015||C>=v&&Math.abs(d-v)<=.02;if(C<=k)_="Road",F="Ch\u1EB7ng 1: Xe t\u1EA3i container v\u1EADn chuy\u1EC3n ra C\u1EA3ng/S\xE2n bay xu\u1EA5t ph\xE1t",M="#FF9500";else if(T){_=s;let f=l&&l.arrival_hub&&l.arrival_hub.name?l.arrival_hub.name:"C\u1EA3ng/S\xE2n bay \u0111\u1EBFn";F="\u0110\xE3 c\u1EADp b\u1EBFn v\xE0 \u0111ang l\xE0m th\u1EE7 t\u1EE5c th\xF4ng quan h\u1EA3i quan t\u1EA1i "+f,M="#28a745"}else if(C<v)_=s,F=s==="Air"?"Ch\u1EB7ng 2: M\xE1y bay v\u1EADn t\u1EA3i \u0111ang bay qua kh\xF4ng ph\u1EADn Qu\u1ED1c t\u1EBF (Air Transit)":"Ch\u1EB7ng 2: T\xE0u container \u0111ang v\u01B0\u1EE3t h\u1EA3i tr\xECnh Th\xE1i B\xECnh D\u01B0\u01A1ng (Ocean Transit)",M=s==="Air"?"#007AFF":"#0055B3";else{_="Road";let f=l&&l.destination&&l.destination.name?l.destination.name:"Kho \u0111\xEDch nh\u1EADn h\xE0ng";F="Ch\u1EB7ng 3: Xe t\u1EA3i container giao nh\u1EADn v\u1EC1 "+f+" (Last-mile Road)",M="#FF9500"}let L=e.getElement?e.getElement():null;if(L){if(e._activeMode!==_){e._activeMode=_;let E=L.querySelector(".lw-vehicle-box");E&&(E.style.borderColor=M);let A=L.querySelector(".lw-vehicle-icon-svg");A&&(A.innerHTML=ee(_))}let f=L.querySelector(".lw-vehicle-icon-svg")||L.querySelector("svg");f&&(f.style.transform=`rotate(${Z}deg)`,f.style.transformOrigin="center center")}if(e._currentProgress=C,g<1)m=requestAnimationFrame(x);else{if(m=null,d<=.001)e.setLatLng(t[0]);else if(Math.abs(d-v)<=.02){let f=l&&l._ahCoord?l._ahCoord:null;!f&&l&&l.arrival_hub&&l.arrival_hub.coordinates&&(f=[l.arrival_hub.coordinates[0],X(l.arrival_hub.coordinates[1],t[t.length-1][1])]),f&&e.setLatLng([f[0],f[1]])}else d>=.999&&e.setLatLng(t[t.length-1]);if(e.getPopup&&e.getPopup()){let f=_==="Ocean"?"T\xE0u bi\u1EC3n \u{1F6A2}":_==="Air"?"M\xE1y bay \u2708\uFE0F":"Xe t\u1EA3i Container \u{1F69A}";e.setPopupContent(`<b>Ph\u01B0\u01A1ng ti\u1EC7n: ${f}</b><br>${F}<br><small>Ti\u1EBFn tr\xECnh to\xE0n tr\xECnh: ${(d*100).toFixed(1)}%</small>`)}}}m=requestAnimationFrame(x)}function X(e,t){if(typeof e!="number"||typeof t!="number")return e;let o=e;for(;o-t>180;)o-=360;for(;o-t<-180;)o+=360;return o}function fe(e,t,o){let n=window.L||window.leaflet;if(!n){$("#lw-map-info-text").html('<span style="color: red;">Th\u01B0 vi\u1EC7n b\u1EA3n \u0111\u1ED3 (Leaflet) ch\u01B0a \u0111\u01B0\u1EE3c t\u1EA3i.</span>');return}if(m&&(cancelAnimationFrame(m),m=null),a){try{a.remove()}catch(h){}a=null,y=null}z=[],J=null,a=n.map("shipment-map",{zoomControl:!0,attributionControl:!0}).setView([20,150],3),window._lw_shipment_map=a,a.on("popupopen",function(h){h&&h.popup&&h.popup._container&&$(h.popup._container).find(".leaflet-popup-close-button").each(function(){$(this).attr("href","javascript:void(0);").attr("role","button").on("click",function(w){return w.preventDefault(),w.stopPropagation(),w.stopImmediatePropagation(),a&&a.closePopup(),!1})})}),n.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",{attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',subdomains:["a","b","c"],maxZoom:19}).addTo(a),le(e.method);let r=e.full_route&&e.full_route.length>0?e.full_route:e.route||[];if(!r||r.length===0){$("#lw-map-info-text").html('<span class="text-muted">Ch\u01B0a c\xF3 t\u1ECDa \u0111\u1ED9 n\xE0o \u0111\u01B0\u1EE3c ghi nh\u1EADn cho \u0111\u01A1n h\xE0ng n\xE0y.</span>');return}let i=D(r,.002);(!i||i.length<2)&&(i=r);let s=[];if(e.legs&&Array.isArray(e.legs)&&e.legs.length>0&&e.legs.forEach(h=>{let w=h.coordinates_latlon||[];if(w.length>=2){let P=D(w,.002);(!P||P.length<2)&&(P=w);let Q=h.mode==="Road",xe=h.mode==="Air",be=Q?"#FF9500":xe?"#007AFF":"#0055B3",we=Q?"6, 8":"",ye=Q?3.5:4,ve=n.polyline(P,{color:be,weight:ye,opacity:.92,dashArray:we}).addTo(a);s.push(ve)}}),s.length===0){let h=n.polyline(i,{color:e.method==="Air"?"#007AFF":e.method==="Ocean"?"#0055B3":"#FF9500",weight:3.5,opacity:.9,dashArray:e.method==="Road"?"6, 8":""}).addTo(a);s.push(h)}try{let h=n.featureGroup(s);a.fitBounds(h.getBounds(),{padding:[40,40],maxZoom:8})}catch(h){}let l=i[0],p=e.origin&&e.origin.name||(typeof e.origin=="string"?e.origin:"Kho nh\xE0 m\xE1y xu\u1EA5t ph\xE1t"),c=n.divIcon({className:"custom-origin-icon",html:'<div style="background: #28a745; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.35); cursor: pointer;" title="\u0110i\u1EC3m xu\u1EA5t ph\xE1t (Origin - \u0110i\u1EC3m O)">O</div>',iconSize:[28,28],iconAnchor:[14,14]}),d=n.marker(l,{icon:c}).addTo(a);d.bindPopup(`<b>Kho xu\u1EA5t ph\xE1t (Origin - \u0110i\u1EC3m O):</b><br>${p}<br><small>To\u1EA1 \u0111\u1ED9: ${l[0].toFixed(4)}, ${l[1].toFixed(4)}</small>`),z.push(d);let u=i[i.length-1],k=e.destination&&e.destination.name||(typeof e.destination=="string"?e.destination:"Kho \u0111\xEDch nh\u1EADn h\xE0ng"),v=n.divIcon({className:"custom-dest-icon",html:'<div style="background: #dc3545; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 800; border: 2.5px solid white; box-shadow: 0 3px 8px rgba(0,0,0,0.35); cursor: pointer;" title="\u0110i\u1EC3m \u0111\xEDch \u0111\u1EBFn (Destination - \u0110i\u1EC3m D)">D</div>',iconSize:[28,28],iconAnchor:[14,14]}),x=n.marker(u,{icon:v}).addTo(a),S=((u[1]+180)%360+360)%360-180;x.bindPopup(`<b>Kho \u0111\xEDch nh\u1EADn h\xE0ng (Destination - \u0110i\u1EC3m D):</b><br>${k}<br><small>To\u1EA1 \u0111\u1ED9: ${u[0].toFixed(4)}, ${S.toFixed(4)}</small>`),z.push(x);let b=null;if(e.legs&&e.legs.length>=1&&e.legs[0].coordinates_latlon&&e.legs[0].coordinates_latlon.length>0){let h=e.legs[0].coordinates_latlon;b=h[h.length-1]}else e.departure_hub&&e.departure_hub.coordinates&&(b=[e.departure_hub.coordinates[0],X(e.departure_hub.coordinates[1],l[1])]);if(b&&e.departure_hub){let h=n.divIcon({className:"custom-dep-hub-icon",html:`<div style="background: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: 2.5px solid ${e.method==="Air"?"#007AFF":"#0055B3"}; box-shadow: 0 2px 6px rgba(0,0,0,0.25); cursor: pointer;" title="Tr\u1EA1m trung chuy\u1EC3n xu\u1EA5t ph\xE1t">
                    ${te(e.method)}
                </div>`,iconSize:[30,30],iconAnchor:[15,15]}),w=n.marker([b[0],b[1]],{icon:h}).addTo(a),P=((b[1]+180)%360+360)%360-180;w.bindPopup(`<b>Tr\u1EA1m trung chuy\u1EC3n xu\u1EA5t ph\xE1t:</b><br>${e.departure_hub.name||"C\u1EA3ng/S\xE2n bay xu\u1EA5t"}<br><small>To\u1EA1 \u0111\u1ED9: ${b[0].toFixed(4)}, ${P.toFixed(4)}</small>`),z.push(w)}let g=null;if(e.legs&&e.legs.length>=2&&e.legs[1].coordinates_latlon&&e.legs[1].coordinates_latlon.length>0){let h=e.legs[1].coordinates_latlon;g=h[h.length-1]}else e.arrival_hub&&e.arrival_hub.coordinates&&(g=[e.arrival_hub.coordinates[0],X(e.arrival_hub.coordinates[1],u[1])]);if(g&&e.arrival_hub){let h=n.divIcon({className:"custom-arr-hub-icon",html:`<div style="background: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; border: 2.5px solid ${e.method==="Air"?"#007AFF":"#0055B3"}; box-shadow: 0 2px 6px rgba(0,0,0,0.25); cursor: pointer;" title="Tr\u1EA1m trung chuy\u1EC3n \u0111\u1EBFn">
                    ${te(e.method)}
                </div>`,iconSize:[30,30],iconAnchor:[15,15]}),w=n.marker([g[0],g[1]],{icon:h}).addTo(a),P=((g[1]+180)%360+360)%360-180;w.bindPopup(`<b>Tr\u1EA1m trung chuy\u1EC3n \u0111\u1EBFn:</b><br>${e.arrival_hub.name||"C\u1EA3ng/S\xE2n bay \u0111\u1EBFn"}<br><small>To\u1EA1 \u0111\u1ED9: ${g[0].toFixed(4)}, ${P.toFixed(4)}</small>`),z.push(w)}e._dhCoord=b,e._ahCoord=g;let I=typeof e.progress=="number"?e.progress:.55,C=e.progress_thresholds||[0,.05,.95,1],O="Road";I>C[1]&&I<=C[2]&&(O=e.method);let Z=O==="Road"?"#FF9500":e.method==="Air"?"#007AFF":"#0055B3",_=V(i),F=W(i,_,0),M=n.divIcon({className:"custom-vehicle-icon",html:`
                <div class="lw-vehicle-box" style="background: white; border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 10px rgba(0,0,0,0.3); border: 2.8px solid ${Z}; transition: border-color 0.3s;">
                    <div class="lw-vehicle-icon-svg" style="display: flex; align-items: center; justify-content: center; transform: rotate(${F.bearing}deg); transform-origin: center center;">
                        ${ee(O)}
                    </div>
                </div>
            `,iconSize:[42,42],iconAnchor:[21,21]}),T=n.marker(F.point,{icon:M,zIndexOffset:1e3}).addTo(a);T._currentProgress=0,T._activeMode=O,T.bindPopup(`<b>V\u1ECB tr\xED ph\u01B0\u01A1ng ti\u1EC7n:</b><br>${e.current_location||"\u0110ang v\u1EADn chuy\u1EC3n"}`),z.push(T),ae(T,i,I,1600,e.legs||[],C,e.method,e),setTimeout(()=>{T&&a&&a.hasLayer(T)&&T.openPopup()},1650);let L=e.method==="Air"?"\u2708\uFE0F \u0110a ph\u01B0\u01A1ng th\u1EE9c H\xE0ng kh\xF4ng (Air)":e.method==="Ocean"?"\u{1F6A2} \u0110a ph\u01B0\u01A1ng th\u1EE9c \u0110\u01B0\u1EDDng bi\u1EC3n (Ocean)":"\u{1F69A} \u0110\u01B0\u1EDDng b\u1ED9 n\u1ED9i \u0111\u1ECBa (Road)",f="#e0f2fe",E="#0369a1",A="\u{1F6A2}";e.progress>=1||e.status_text&&(e.status_text.includes("giao h\xE0ng th\xE0nh c\xF4ng")||e.status_text.includes("Ho\xE0n th\xE0nh"))?(f="#dcfce7",E="#15803d",A="\u2705"):e.status_text&&(e.status_text.includes("th\xF4ng quan")||e.status_text.includes("H\u1EA3i quan")||e.status_text.includes("Customs"))?(f="#fef3c7",E="#b45309",A="\u{1F3DB}\uFE0F"):e.method==="Air"&&(A="\u2708\uFE0F");let me=`
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <!-- T\u1EA7ng 1: Banner Tr\u1EA1ng th\xE1i v\u1EADn h\xE0nh -->
                <div style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; padding: 7px 12px; border-radius: 6px; border: 1px solid #e2e8f0; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                    <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; color: #64748b;">Tr\u1EA1ng th\xE1i v\u1EADn h\xE0nh</span>
                    <span class="badge" style="background: ${f}; color: ${E}; font-size: 11.5px; font-weight: 600; padding: 4px 10px; border-radius: 10px; white-space: normal; text-align: right; line-height: 1.3; max-width: 72%;">
                        ${A} ${e.status_text}
                    </span>
                </div>

                <!-- T\u1EA7ng 2: 2 Kh\u1ED1i 50-50 C\xE2n x\u1EE9ng -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div style="background: #ffffff; padding: 9px 12px; border-radius: 6px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div>
                            <div style="font-size: 10.5px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 2px;">M\xF4 h\xECnh v\u1EADn t\u1EA3i</div>
                            <div style="font-size: 12px; font-weight: 600; color: #0f172a; line-height: 1.3;">${L}</div>
                        </div>
                        <div style="font-size: 11.5px; color: #0284c7; font-weight: 600; margin-top: 4px;">
                            C\u1EF1 ly: ${Math.round(e.distance_km||0).toLocaleString()} km
                        </div>
                    </div>

                    <div style="background: #ffffff; padding: 9px 12px; border-radius: 6px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 1px 2px rgba(0,0,0,0.02);">
                        <div>
                            <div style="font-size: 10.5px; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 2px;">V\u1ECB tr\xED hi\u1EC7n t\u1EA1i</div>
                            <div style="font-size: 12px; font-weight: 600; color: #0284c7; line-height: 1.3; word-break: break-word;" title="${e.current_location}">
                                \u{1F4CD} ${e.current_location}
                            </div>
                        </div>
                        <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                            Ti\u1EBFn tr\xECnh: <strong style="color: #0284c7;">${Math.round((e.progress||0)*100)}%</strong>
                        </div>
                    </div>
                </div>
            </div>
        `;$("#lw-map-info-text").html(me),ge(t,o,e),setTimeout(()=>{a&&a.invalidateSize()},300)}function ge(e,t,o){let n=$("#lw-timeline-container");if(o&&o.checkpoints&&o.checkpoints.length>0){H(o.checkpoints,n,o);return}if(window.cur_frm&&cur_frm.doc&&cur_frm.doc.name===e&&cur_frm.doc.transit_route&&cur_frm.doc.transit_route.length>0){H(cur_frm.doc.transit_route,n,o);return}let r=t,i=e;t==="Purchase Order"?frappe.db.get_value("Shipment Tracking",{purchase_order:e},"name").then(s=>{s&&s.message&&s.message.name?frappe.db.get_doc("Shipment Tracking",s.message.name).then(l=>{H(l.transit_route||[],n,o)}):n.html('<div style="color: #8d99a6; font-size: 12px; padding: 8px 0;">Ch\u01B0a li\xEAn k\u1EBFt phi\u1EBFu Shipment Tracking ho\u1EB7c ch\u01B0a c\xF3 l\u1ED9 tr\xECnh chi ti\u1EBFt.</div>')}):t==="Shipment Tracking"?frappe.db.get_doc("Shipment Tracking",e).then(s=>{H(s.transit_route||[],n,o)}):n.html('<div style="color: #8d99a6; font-size: 12px; padding: 8px 0;">Kh\xF4ng c\xF3 d\u1EEF li\u1EC7u l\u1ED9 tr\xECnh.</div>')}function H(e,t,o){if(!e||e.length===0){t.html('<div style="color: #8d99a6; font-size: 12px; padding: 8px 0;">Ch\u01B0a c\xF3 tr\u1EA1m l\u1ED9 tr\xECnh n\xE0o.</div>');return}let n=e.some(i=>i.is_current===!0||i.activity&&i.activity.includes("(Current Position)")),r='<div class="lw-timeline">';e.forEach((i,s)=>{let l=s===e.length-1,p=i.is_current===!0||i.activity&&i.activity.includes("(Current Position)")||!n&&l,c=(i.activity||"").replace(" (Current Position)","").replace("(Current Position)","").trim(),d=p?"lw-timeline-item current-step":"lw-timeline-item completed",u=p?'<span class="lw-timeline-current-badge">\u{1F4CD} V\u1ECB tr\xED hi\u1EC7n t\u1EA1i</span>':"";r+=`
                <div class="${d}">
                    <div class="lw-timeline-node"></div>
                    <div class="lw-timeline-date">${i.date||""}</div>
                    <div class="lw-timeline-title">
                        <span>${c}</span>
                        ${u}
                    </div>
                    <div class="lw-timeline-desc">\u{1F4CD} ${i.location||""}</div>
                    ${i.notes?`<div class="lw-timeline-notes">${i.notes}</div>`:""}
                </div>
            `}),r+="</div>",t.html(r)}function G(e,t=!1){if((!e||e!=="import"&&e!=="export")&&(e="import"),B=e,e==="export"?($("#lw-tab-export").addClass("active").css({background:"#ffffff",color:"#0071E3","font-weight":"600","box-shadow":"0 1px 3px rgba(0,0,0,0.08)"}),$("#lw-tab-import").removeClass("active").css({background:"transparent",color:"#495057","font-weight":"500","box-shadow":"none"}),$("#lw-import-step-list").hide(),$("#lw-export-step-list").show()):($("#lw-tab-import").addClass("active").css({background:"#ffffff",color:"#0071E3","font-weight":"600","box-shadow":"0 1px 3px rgba(0,0,0,0.08)"}),$("#lw-tab-export").removeClass("active").css({background:"transparent",color:"#495057","font-weight":"500","box-shadow":"none"}),$("#lw-export-step-list").hide(),$("#lw-import-step-list").show()),t){let o=typeof frappe!="undefined"&&frappe.get_route?frappe.get_route():[];o&&o[0]==="Form"&&o[1]&&o[2]&&frappe.call({method:"logistics_wizard.api.get_workflow_chain_status",args:{doctype:o[1],docname:o[2],flow_type:B},callback:function(n){n&&n.message&&n.message.success&&pe(n.message.steps,B)}})}}function Y(){[...R,...j].forEach(t=>{let o=$("#"+t.id);if(o.length){o.removeClass("wiz-step-completed wiz-step-current wiz-step-pending"),o.find(".wiz-check-badge").html("");let n=o.find("a");n.attr("href","/app/"+t.slug),n.text(t.label)}})}function pe(e,t){if(!e||!e.length)return;let n=(t||B)==="export"?j:R;e.forEach((r,i)=>{let s=n[i];if(!s)return;let l=$("#"+s.id);if(!l.length)return;let p=r.label||s.label,c=r.url||"/app/"+s.slug,d=l.find("a");d.attr("href",c),d.text(p),r.completed?(l.addClass("wiz-step-completed"),l.find(".wiz-check-badge").html("\u2714")):r.is_current?l.addClass("wiz-step-current"):l.addClass("wiz-step-pending"),r.is_current&&l.addClass("wiz-step-current")})}function ce(){if(N(),typeof frappe=="undefined"||!frappe.get_route)return;let e=frappe.get_route();if(!(!e||!e.length))if(e[0]==="Form"&&e[1]&&K.includes(e[1])&&e[2]){let t=e[1],o=e[2],n=null;q.includes(t)?n="export":U.includes(t)&&(n="import"),frappe.call({method:"logistics_wizard.api.get_workflow_chain_status",args:{doctype:t,docname:o,flow_type:n},callback:function(r){if(Y(),r&&r.message&&r.message.success){let i=r.message.flow_type||n||"import";G(i,!1),pe(r.message.steps,i)}}})}else if(e[0]==="List"&&e[1]&&K.includes(e[1])){Y();let t=e[1],o=q.includes(t)?"export":"import";G(o,!1);let n=(o==="export"?"wiz-exp-":"wiz-")+t.replace(/\s+/g,"-");$("#"+n).addClass("wiz-step-current")}else Y()}typeof frappe!="undefined"&&frappe.router&&frappe.router.on("change",function(){N(),ce()}),window.LogisticsWizardMap={douglasPeucker:D,perpendicularDistance:se,calculateBearing:re,computePolylineMetrics:V,interpolateAtProgress:W,animateVehicle:ae,update_marine_overlay:le,getShipmentMap:function(){return a},getSeaOverlayLayer:function(){return y},getMapPolyline:function(){return J},getMapMarkers:function(){return z}},N(),setTimeout(ce,300),setTimeout(N,1e3)}document.readyState==="loading"?$(document).ready(de):de();})();
//# sourceMappingURL=smart_workflow_widget.bundle.NYYA6EOX.js.map
