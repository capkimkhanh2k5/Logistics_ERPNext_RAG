#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_logistics_ai_chatbot_ui.py
================================
Unit test suite verifying the complete frontend architecture of the
Logistics AI Chatbot page (ChatGPT / Gemini / Claude inspired UI).
"""

import os
import json
import unittest
import re

PAGE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "apps",
        "logistics_wizard",
        "logistics_wizard",
        "page",
        "logistics_ai_chatbot"
    )
)


class TestLogisticsAIChatbotUI(unittest.TestCase):
    def test_01_all_page_files_exist(self):
        """Kiểm tra sự hiện diện đầy đủ của 4 file cấu thành Page Desk"""
        required_files = [
            "logistics_ai_chatbot.json",
            "logistics_ai_chatbot.html",
            "logistics_ai_chatbot.css",
            "logistics_ai_chatbot.js"
        ]
        for f in required_files:
            fpath = os.path.join(PAGE_DIR, f)
            self.assertTrue(os.path.exists(fpath), f"Thiếu file: {f}")
            self.assertGreater(os.path.getsize(fpath), 100, f"File quá nhỏ hoặc rỗng: {f}")

    def test_02_json_page_config(self):
        """Xác thực cấu hình DocType Page JSON"""
        json_path = os.path.join(PAGE_DIR, "logistics_ai_chatbot.json")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data.get("doctype"), "Page")
        self.assertEqual(data.get("page_name"), "logistics-ai-chatbot")
        self.assertIn(data.get("title"), ["Logistics AI ChatBot", "Logistics AI Copilot"])

    def test_03_html_dom_elements(self):
        """Xác thực đầy đủ các phần tử DOM then chốt theo chuẩn ChatGPT/Gemini/Claude"""
        html_path = os.path.join(PAGE_DIR, "logistics_ai_chatbot.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        required_elements = [
            'id="logistics-ai-chat-app"',
            'id="chat-sidebar"',
            'id="btn-new-chat"',
            'id="chat-search-input"',
            'id="chat-model-selector"',
            'id="chat-welcome-screen"',
            'class="quick-prompts-grid"',
            'id="chat-messages-container"',
            'class="chat-input-wrapper"',
            'id="chat-textarea"',
            'id="btn-send-message"',
            'id="btn-stop-generation"',
            'id="btn-attach-file"',
            'id="chat-settings-modal"',
            'id="tab-provider"',
            'id="tab-developer"'
        ]
        for el in required_elements:
            self.assertIn(el, content, f"DOM thiếu phần tử quan trọng: {el}")

    def test_04_css_styling_and_purple_ban(self):
        """Xác thực CSS hoàn chỉnh và không vi phạm Purple Ban"""
        css_path = os.path.join(PAGE_DIR, "logistics_ai_chatbot.css")
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Kiểm tra từ khóa cấm
        forbidden = re.compile(r"\b(purple|violet|magenta|indigo|plum|fuchsia)\b", re.IGNORECASE)
        # Bỏ qua comments
        clean_css = re.sub(r"/\*[\s\S]*?\*/", "", content)
        matches = forbidden.findall(clean_css)
        self.assertEqual(matches, [], f"Phát hiện từ khóa màu tím trong CSS: {matches}")

        # Kiểm tra các class styling chính
        self.assertIn(".chat-app-container", content)
        self.assertIn(".chat-sidebar", content)
        self.assertIn(".chat-top-bar", content)
        self.assertIn(".quick-prompt-card", content)
        self.assertIn(".thinking-accordion", content)
        self.assertIn(".tool-call-card", content)
        self.assertIn(".chat-input-box", content)

    def test_05_js_controller_and_bridge(self):
        """Xác thực controller JS và cổng kết nối Developer Hook Bridge"""
        js_path = os.path.join(PAGE_DIR, "logistics_ai_chatbot.js")
        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("frappe.pages['logistics-ai-chatbot']", content)
        self.assertIn("class LogisticsAIChatbotUI", content)
        self.assertIn("window.LogisticsChatbotBridge", content)
        self.assertIn("onSendMessage", content)
        self.assertIn("onThinking", content)
        self.assertIn("onToolCall", content)
        self.assertIn("onStreamChunk", content)
        self.assertIn("onComplete", content)


if __name__ == "__main__":
    unittest.main()
